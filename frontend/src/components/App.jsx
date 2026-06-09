import { AlertTriangle, FilePlus2, GitMerge, RefreshCw, Trash2, Upload } from "./FontAwesomeIcons";
import { useEffect, useRef, useState } from "react";
import { deleteJSON, getBlob, getJSON, patchJSON, postForm, postJSON } from "../api/client";
import { AboutPage } from "./AboutPage";
import { ActionStrip } from "./ActionStrip";
import { ChangePasswordDialog } from "./ChangePasswordDialog";
import { ConfirmDialog } from "./ConfirmDialog";
import { ConceptMapPanel } from "./ConceptMapPanel";
import { GeneratedDocumentsView } from "./GeneratedDocumentsView";
import { Manuscript } from "./Manuscript";
import { LoginPage } from "./LoginPage";
import { OutlinePanel } from "./OutlinePanel";
import { Sidebar } from "./Sidebar";
import { SettingsPanel } from "./SettingsPanel";
import { TopBar } from "./TopBar";
import { WorkspaceHeader } from "./WorkspaceHeader";

const AUTH_STORAGE_KEY = "discourse2draft.authSession";

function loadStoredAuthSession() {
  if (typeof window === "undefined") return null;
  try {
    const storedSession = window.localStorage.getItem(AUTH_STORAGE_KEY);
    return storedSession ? JSON.parse(storedSession) : null;
  } catch (error) {
    window.localStorage.removeItem(AUTH_STORAGE_KEY);
    return null;
  }
}

function saveStoredAuthSession(sessionPayload) {
  if (typeof window === "undefined") return;
  try {
    if (!sessionPayload) {
      window.localStorage.removeItem(AUTH_STORAGE_KEY);
      return;
    }
    window.localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(sessionPayload));
  } catch (error) {
    window.localStorage.removeItem(AUTH_STORAGE_KEY);
  }
}

function formatDocumentDate(value) {
  if (!value) return "";

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;

  return date.toLocaleString();
}

function generatedFileToDocument(file = {}) {
  const name = file.name ?? file.file_name ?? "Untitled";
  const lastModified = file.last_modified ?? file.update_date ?? file.date ?? file.create_date;

  return {
    ...file,
    id: file.id,
    name,
    file_name: file.file_name ?? name,
    date: formatDocumentDate(lastModified),
    last_modified: formatDocumentDate(lastModified),
    status: file.status,
    session: file.session,
    settings_id: file.settings_id,
    ai_architecture: file.ai_architecture,
  };
}

function normalizeGeneratedDocuments(documents = []) {
  return documents.map(generatedFileToDocument);
}

function normalizeUploadedDocuments(documents = []) {
  return documents.map((document) => ({
    ...document,
    name: document.name ?? document.file_name,
    date: formatDocumentDate(document.date ?? document.update_date ?? document.create_date),
    type: document.type ?? "file",
  }));
}

function normalizeReferenceList(refList = []) {
  const seen = new Set();
  return (Array.isArray(refList) ? refList : [])
    .map((reference) => String(reference ?? "").trim())
    .filter((reference) => {
      if (!reference || seen.has(reference)) return false;
      seen.add(reference);
      return true;
    });
}

function hasManuscriptContent(manuscript = [], generatedContent = "") {
  if (String(generatedContent ?? "").trim()) return true;
  return (Array.isArray(manuscript) ? manuscript : []).some((section) => String(section?.body ?? "").trim());
}

function wait(milliseconds) {
  return new Promise((resolve) => {
    window.setTimeout(resolve, milliseconds);
  });
}

function generationStatusMessage(job = {}) {
  if (job.status === "completed") return job.message || "Content generation completed.";
  if (job.status === "error") return job.error || job.message || "Content generation stopped.";
  if (job.status === "paused") return job.message || "Generation paused. Click Generate to continue.";

  const completed = Number(job.completed_sections ?? 0);
  const total = Number(job.total_sections ?? 0);
  if (job.current_section && total > 0) {
    return `Writing section ${Math.min(completed + 1, total)} of ${total}: ${job.current_section}`;
  }

  return job.message || "Preparing content generation...";
}

function inlineActionProgressMessage(action) {
  if (action === "Expand") return "Expanding selected paragraph...";
  if (action === "Rephrase") return "Rephrasing selected paragraph...";
  if (action === "Remove") return "Removing selected paragraph...";
  return "Updating selected paragraph...";
}

function authOwnerQuery(authSession) {
  const params = new URLSearchParams();
  if (authSession?.user?.email) {
    params.set("email", authSession.user.email);
  } else if (authSession?.session) {
    params.set("session", authSession.session);
  }
  return params.toString();
}

function safeDownloadName(value) {
  return (value || "generated-document").replace(/[^a-z0-9_-]+/gi, "-").replace(/^-+|-+$/g, "") || "generated-document";
}

function downloadBlobFile(fileName, blob) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = fileName;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

export function App() {
  const initialAuthSession = useRef(loadStoredAuthSession()).current;
  const outlineBeforeExample = useRef("");
  const pauseRequestedRef = useRef(false);
  const activeGenerationJobRef = useRef("");
  const [showLogin, setShowLogin] = useState(!initialAuthSession);
  const [authSession, setAuthSession] = useState(initialAuthSession);
  const [aiSettings, setAiSettings] = useState(initialAuthSession?.settings ?? null);
  const [llmOptions, setLlmOptions] = useState(initialAuthSession?.llm_options ?? []);
  const [isSettingsPanelOpen, setIsSettingsPanelOpen] = useState(false);
  const [isChangePasswordOpen, setIsChangePasswordOpen] = useState(false);
  const [isAboutOpen, setIsAboutOpen] = useState(false);
  const [isConceptMapOpen, setIsConceptMapOpen] = useState(false);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [isGeneratedDocumentsViewOpen, setIsGeneratedDocumentsViewOpen] = useState(false);
  const [isRegenerateConfirmOpen, setIsRegenerateConfirmOpen] = useState(false);
  const [systemHealth, setSystemHealth] = useState(null);
  const [isHealthLoading, setIsHealthLoading] = useState(false);
  const [isSavingSettings, setIsSavingSettings] = useState(false);
  const [isSavingOutline, setIsSavingOutline] = useState(false);
  const [isSavingFile, setIsSavingFile] = useState(false);
  const [isConfiguringLiteratureSearch, setIsConfiguringLiteratureSearch] = useState(false);
  const [isLoadingGeneratedDocuments, setIsLoadingGeneratedDocuments] = useState(false);
  const [isLoadingUploadedDocuments, setIsLoadingUploadedDocuments] = useState(false);
  const [isUploadingDocuments, setIsUploadingDocuments] = useState(false);
  const [isAttachingUploadedDocuments, setIsAttachingUploadedDocuments] = useState(false);
  const [generatedFile, setGeneratedFile] = useState(null);
  const [uploadReplacePrompt, setUploadReplacePrompt] = useState(null);
  const [attachFilesPrompt, setAttachFilesPrompt] = useState(null);
  const [removeAttachedFilePrompt, setRemoveAttachedFilePrompt] = useState(null);
  const [deleteUploadedFilePrompt, setDeleteUploadedFilePrompt] = useState(null);
  const [deleteGeneratedFilePrompt, setDeleteGeneratedFilePrompt] = useState(null);
  const [enableLiteratureSearchPrompt, setEnableLiteratureSearchPrompt] = useState(null);
  const [disableLiteratureSearchPrompt, setDisableLiteratureSearchPrompt] = useState(null);
  const [literatureCollectionName, setLiteratureCollectionName] = useState("");
  const [isLiteratureSearchEnabled, setIsLiteratureSearchEnabled] = useState(false);
  const [fileName, setFileName] = useState("");
  const [query, setQuery] = useState("");
  const [referenceDocument, setReferenceDocument] = useState(null);
  const [outlineMode, setOutlineMode] = useState("outline");
  const [outline, setOutline] = useState("");
  const [useExample, setUseExample] = useState(false);
  const [action, setAction] = useState("Expand");
  const [status, setStatus] = useState("");
  const [generatedContent, setGeneratedContent] = useState("");
  const [currentWritingSection, setCurrentWritingSection] = useState("");
  const [currentGenerationJobId, setCurrentGenerationJobId] = useState("");
  const [selectedParagraph, setSelectedParagraph] = useState(null);
  const [updatingParagraphId, setUpdatingParagraphId] = useState("");
  const [workspaceResetVersion, setWorkspaceResetVersion] = useState(0);
  const [isWriting, setIsWriting] = useState(false);
  const [workspaceData, setWorkspaceData] = useState({
    manuscript: [],
    ref_list: [],
    concept_maps: [],
    generated_documents: [],
    uploaded_documents: [],
    attached_files: [],
  });

  useEffect(() => {
    let isMounted = true;

    async function loadSystemHealth(showLoading = false) {
      if (showLoading) {
        setIsHealthLoading(true);
      }
      try {
        const payload = await getJSON("/api/health");
        if (isMounted) {
          setSystemHealth(payload);
        }
      } catch (error) {
        if (isMounted) {
          setSystemHealth({
            status: "error",
            checks: {
              ai_model: { status: "unknown", message: "Health could not be checked." },
              chroma_db: { status: "unknown", message: "Health could not be checked." },
              postgres: { status: "unknown", message: "Health could not be checked." },
            },
          });
        }
      } finally {
        if (isMounted && showLoading) {
          setIsHealthLoading(false);
        }
      }
    }

    async function loadWorkspaceData() {
      try {
        const payload = await getJSON("/api/workspace");
        if (!isMounted) return;
        setWorkspaceData((current) => ({
          ...current,
          manuscript: current.manuscript?.length ? current.manuscript : (payload.manuscript ?? []),
          ref_list: current.ref_list?.length ? current.ref_list : normalizeReferenceList(payload.ref_list),
          generated_documents: current.generated_documents?.length ? current.generated_documents : (payload.generated_documents ?? []),
          uploaded_documents: current.uploaded_documents?.length ? current.uploaded_documents : (payload.uploaded_documents ?? []),
        }));
        setOutline(payload.outline_template ?? "");
      } catch (error) {
        if (isMounted) {
          setStatus(error.message);
        }
      }
    }

    loadSystemHealth(true);
    loadWorkspaceData();
    const healthInterval = window.setInterval(() => loadSystemHealth(false), 30000);

    return () => {
      isMounted = false;
      window.clearInterval(healthInterval);
    };
  }, []);

  useEffect(() => {
    if (!authSession?.user?.email && !authSession?.session) return undefined;

    let isMounted = true;

    async function loadWorkspaceSessionData() {
      setIsLoadingGeneratedDocuments(true);
      setIsLoadingUploadedDocuments(true);
      try {
        const email = authSession.user?.email ? encodeURIComponent(authSession.user.email) : "";
        const session = encodeURIComponent(authSession.session);
        const settingsId = authSession.settings?.id;
        const generatedQuery = authOwnerQuery(authSession);
        const uploadedQuery = authOwnerQuery(authSession);
        const [generatedPayload, uploadedPayload, settingsPayload] = await Promise.all([
          generatedQuery ? getJSON(`/api/generated-files?${generatedQuery}&limit=1000`) : Promise.resolve({ generated_documents: [] }),
          uploadedQuery ? getJSON(`/api/uploaded-files?${uploadedQuery}`) : Promise.resolve({ uploaded_documents: [] }),
          settingsId && email ? getJSON(`/api/settings/${settingsId}?email=${email}&session=${session}`) : Promise.resolve({}),
        ]);
        if (!isMounted) return;
        if (settingsPayload.settings) {
          setAiSettings(settingsPayload.settings);
          setLlmOptions(settingsPayload.llm_options ?? []);
        }
        setWorkspaceData((current) => ({
          ...current,
          generated_documents: normalizeGeneratedDocuments(generatedPayload.generated_documents),
          uploaded_documents: normalizeUploadedDocuments(uploadedPayload.uploaded_documents),
        }));
      } catch (error) {
        if (isMounted) {
          setStatus(error.message);
        }
      } finally {
        if (isMounted) {
          setIsLoadingGeneratedDocuments(false);
          setIsLoadingUploadedDocuments(false);
        }
      }
    }

    loadWorkspaceSessionData();

    return () => {
      isMounted = false;
    };
  }, [authSession]);

  useEffect(() => {
    if (showLogin || authSession?.user?.email || authSession?.status === "anonymous") return undefined;

    let isMounted = true;

    async function loadDefaultSettings() {
      try {
        const payload = await getJSON("/api/settings/default");
        if (!isMounted) return;
        setAiSettings(payload.settings);
        setLlmOptions(payload.llm_options ?? []);
      } catch (error) {
        if (isMounted) {
          setStatus(error.message);
        }
      }
    }

    loadDefaultSettings();

    return () => {
      isMounted = false;
    };
  }, [showLogin, authSession]);

  async function generateOutline() {
    setStatus("Generating outline...");
    try {
      const payload = await postJSON("/api/ai/outline", {
        query: query.trim() || fileName,
        model_name: aiSettings?.llm,
        temperature: Number(aiSettings?.temperature ?? 0),
        instructions: aiSettings?.instructions ?? "",
      });
      const content = payload.result?.content ?? payload.result?.result?.content ?? "";
      setOutline(content || outline);
      setOutlineMode("outline");
      setStatus("Outline generated");
    } catch (error) {
      setStatus(error.message);
    }
  }

  async function formatOutline() {
    setStatus("Formatting outline...");
    try {
      const payload = await postJSON("/api/ai/outline/format", {
        outline_unstructured: outline,
        model_name: aiSettings?.llm,
        temperature: Number(aiSettings?.temperature ?? 0),
        instructions: aiSettings?.instructions ?? "",
      });
      const content = payload.result?.content ?? "";
      setOutline(content || outline);
      setStatus("Outline formatted");
    } catch (error) {
      setStatus(error.message);
    }
  }

  async function setUseExampleOutline(checked) {
    if (!checked) {
      setUseExample(false);
      setOutline(outlineBeforeExample.current);
      outlineBeforeExample.current = "";
      return;
    }

    outlineBeforeExample.current = outline;
    setUseExample(true);
    setStatus("Loading example outline...");
    try {
      const payload = await getJSON("/api/outline-templates/example");
      setOutline(payload.content ?? "");
      setStatus("Example outline loaded");
    } catch (error) {
      setUseExample(false);
      setStatus(error.message);
    }
  }

  function updateOutlineFromEditor(nextOutline) {
    if (useExample) {
      setUseExample(false);
      outlineBeforeExample.current = "";
    }
    setOutline(nextOutline);
  }

  async function writeContent() {
    if (!generatedFile?.id) {
      setStatus("Save this file before starting content generation.");
      return;
    }

    if (!selectedParagraph?.text) {
      setStatus("Select a manuscript paragraph before running an inline action.");
      return;
    }

    setIsWriting(true);
    setUpdatingParagraphId(selectedParagraph.id);
    setStatus(inlineActionProgressMessage(action));
    try {
      const payload = await patchJSON(`/api/generated-files/${generatedFile.id}/paragraph`, {
        action,
        section_path: selectedParagraph.path ?? [],
        section_heading: selectedParagraph.heading ?? "",
        paragraph_index: selectedParagraph.paragraphIndex,
        raw_paragraph: selectedParagraph.rawText ?? selectedParagraph.text,
        email: authSession?.user?.email ?? null,
        session: authSession?.session ?? null,
        model_name: aiSettings?.llm,
        temperature: Number(aiSettings?.temperature ?? 0),
        instructions: aiSettings?.instructions ?? "",
      });
      setWorkspaceData((current) => ({
        ...current,
        manuscript: payload.manuscript ?? current.manuscript,
        ref_list: normalizeReferenceList(payload.ref_list ?? current.ref_list),
      }));
      if (payload.outline !== undefined) {
        setOutline(payload.outline ?? "");
      }
      if (payload.generated_file) {
        const nextGeneratedFile = generatedFileToDocument(payload.generated_file);
        setGeneratedFile(nextGeneratedFile);
        setWorkspaceData((current) => ({
          ...current,
          generated_documents: current.generated_documents.map((document) =>
            document.id === nextGeneratedFile.id ? { ...document, ...nextGeneratedFile } : document,
          ),
        }));
      }
      setGeneratedContent("");
      setSelectedParagraph(null);
      setStatus(payload.message ?? "Paragraph updated.");
    } catch (error) {
      setStatus(error.message);
    } finally {
      setIsWriting(false);
      setUpdatingParagraphId("");
    }
  }

  async function runStructuredOutline(mode = "remaining") {
    if (!generatedFile?.id) {
      setStatus("Save this file before running the structured outline.");
      return;
    }

    if (!outline.trim()) {
      setStatus("Add a structured outline before running it.");
      return;
    }

    let jobId = "";
    pauseRequestedRef.current = false;
    setIsSavingOutline(true);
    setGeneratedContent("");
    setCurrentWritingSection("");
    setCurrentGenerationJobId("");
    setSelectedParagraph(null);
    setStatus("Saving structured outline...");
    try {
      const payload = await postJSON(`/api/generated-files/${generatedFile.id}/generate`, {
        outline,
        email: authSession?.user?.email ?? null,
        session: authSession?.user?.email ? null : (authSession?.session ?? null),
        mode,
        architecture_type: generatedFile.ai_architecture ?? "base",
        collection_name_lit_search: isLiteratureSearchEnabled ? literatureCollectionName : "",
        model_name: aiSettings?.llm,
        temperature: Number(aiSettings?.temperature ?? 0),
        instructions: aiSettings?.instructions ?? "",
      });
      let job = payload.job;
      jobId = job?.id ?? "";
      activeGenerationJobRef.current = jobId;
      setCurrentGenerationJobId(jobId);
      const savedFile = job?.generated_file ?? generatedFile;
      setGeneratedFile(savedFile);
      setWorkspaceData((current) => {
        const generatedDocuments = current.generated_documents ?? [];
        return {
          ...current,
          manuscript: job?.manuscript ?? current.manuscript,
          ref_list: normalizeReferenceList(job?.ref_list ?? current.ref_list),
          generated_documents: generatedDocuments.map((document) =>
            String(document.id) === String(savedFile.id)
              ? {
                  ...document,
                  date: formatDocumentDate(savedFile.update_date),
                  name: savedFile.file_name ?? document.name,
                  status: savedFile.status ?? "running",
                }
              : document,
          ),
        };
      });
      setCurrentWritingSection(job?.current_section ?? "");
      setStatus(generationStatusMessage(job));

      while ((job?.status === "queued" || job?.status === "running") && !pauseRequestedRef.current) {
        await wait(1200);
        if (pauseRequestedRef.current) break;
        const jobPayload = await getJSON(`/api/generation-jobs/${job.id}`);
        if (pauseRequestedRef.current) break;
        job = jobPayload.job;
        setCurrentWritingSection(job?.current_section ?? "");
        setStatus(generationStatusMessage(job));
        setWorkspaceData((current) => {
          const generatedDocuments = current.generated_documents ?? [];
          return {
            ...current,
            manuscript: job?.manuscript ?? current.manuscript,
            ref_list: normalizeReferenceList(job?.ref_list ?? current.ref_list),
            generated_documents: generatedDocuments.map((document) =>
              String(document.id) === String(savedFile.id)
                ? {
                    ...document,
                    status: job?.generated_file?.status ?? document.status,
                  }
                : document,
            ),
          };
        });
      }

      if (pauseRequestedRef.current) {
        setCurrentWritingSection("");
        if (activeGenerationJobRef.current === jobId) {
          setStatus("Generation paused. Click Generate to continue with the remaining outline.");
        }
        return;
      }

      if (job?.status === "error") {
        throw new Error(job.error || "Content generation stopped before it finished.");
      }

      if (job?.generated_file) {
        setGeneratedFile(job.generated_file);
      }
      setCurrentWritingSection("");
      setStatus(generationStatusMessage(job));
    } catch (error) {
      setCurrentWritingSection("");
      setStatus(error.message);
    } finally {
      if (!jobId || activeGenerationJobRef.current === jobId) {
        activeGenerationJobRef.current = "";
        setCurrentGenerationJobId("");
        setIsSavingOutline(false);
      }
    }
  }

  function regenerateStructuredOutline() {
    if (!generatedFile?.id) {
      setStatus("Save this file before regenerating the manuscript.");
      return;
    }

    if (!hasManuscriptContent(workspaceData.manuscript, generatedContent)) {
      setStatus("Generate manuscript content before using Regenerate.");
      return;
    }

    if (!outline.trim()) {
      setStatus("Add a structured outline before regenerating the manuscript.");
      return;
    }

    setIsRegenerateConfirmOpen(true);
  }

  async function confirmRegenerateStructuredOutline() {
    setIsRegenerateConfirmOpen(false);
    await runStructuredOutline("restart");
  }

  async function pauseStructuredOutline() {
    const jobId = currentGenerationJobId || activeGenerationJobRef.current;
    if (!jobId) return;

    pauseRequestedRef.current = true;
    activeGenerationJobRef.current = "";
    setCurrentGenerationJobId("");
    setCurrentWritingSection("");
    setIsSavingOutline(false);
    setStatus("Generation paused. Click Generate to continue with the remaining outline.");
    try {
      const payload = await postJSON(`/api/generation-jobs/${jobId}/pause`, {});
      setStatus(payload.job?.message || generationStatusMessage(payload.job));
    } catch (error) {
      setStatus(error.message);
    }
  }

  function resetDocumentWorkspace(nextStatus = "") {
    pauseRequestedRef.current = true;
    activeGenerationJobRef.current = "";
    setGeneratedFile(null);
    setLiteratureCollectionName("");
    setIsLiteratureSearchEnabled(false);
    setFileName("");
    setQuery("");
    setReferenceDocument(null);
    setOutlineMode("outline");
    setOutline("");
    setUseExample(false);
    outlineBeforeExample.current = "";
    setAction("Expand");
    setGeneratedContent("");
    setCurrentWritingSection("");
    setCurrentGenerationJobId("");
    setSelectedParagraph(null);
    setIsWriting(false);
    setIsSavingFile(false);
    setIsSavingOutline(false);
    setIsConfiguringLiteratureSearch(false);
    setIsAttachingUploadedDocuments(false);
    setUploadReplacePrompt(null);
    setAttachFilesPrompt(null);
    setRemoveAttachedFilePrompt(null);
    setDeleteGeneratedFilePrompt(null);
    setDisableLiteratureSearchPrompt(null);
    setIsConceptMapOpen(false);
    setIsRegenerateConfirmOpen(false);
    setWorkspaceResetVersion((current) => current + 1);
    setWorkspaceData((current) => ({
      ...current,
      manuscript: [],
      ref_list: [],
      concept_maps: [],
      attached_files: [],
    }));
    setStatus(nextStatus);
  }

  async function newDocument() {
    const jobId = currentGenerationJobId || activeGenerationJobRef.current;
    resetDocumentWorkspace("");

    if (!jobId) return;
    try {
      await postJSON(`/api/generation-jobs/${jobId}/pause`, {});
    } catch (error) {
      setStatus(error.message);
    }
  }

  function enterWorkspace(payload = null) {
    let sessionPayload = payload;
    if (payload?.status === "anonymous" && !payload?.session) {
      const anonymousSession = payload?.settings?.session ?? crypto.randomUUID();
      sessionPayload = {
        ...payload,
        session: anonymousSession,
        settings: {
          ...(payload?.settings ?? {}),
          session: anonymousSession,
        },
      };
    }

    setAuthSession(sessionPayload);
    saveStoredAuthSession(sessionPayload);
    setAiSettings(sessionPayload?.settings ?? null);
    setLlmOptions(sessionPayload?.llm_options ?? []);
    setShowLogin(false);
  }

  function logout() {
    saveStoredAuthSession(null);
    setAuthSession(null);
    setAiSettings(null);
    setLlmOptions([]);
    setGeneratedFile(null);
    setLiteratureCollectionName("");
    setIsLiteratureSearchEnabled(false);
    setFileName("");
    setReferenceDocument(null);
    setGeneratedContent("");
    setCurrentWritingSection("");
    setCurrentGenerationJobId("");
    setSelectedParagraph(null);
    setIsConceptMapOpen(false);
    setIsGeneratedDocumentsViewOpen(false);
    setIsSavingFile(false);
    setIsHealthLoading(false);
    setIsSavingOutline(false);
    setIsConfiguringLiteratureSearch(false);
    setIsLoadingGeneratedDocuments(false);
    setIsLoadingUploadedDocuments(false);
    setIsUploadingDocuments(false);
    setIsAttachingUploadedDocuments(false);
    setUploadReplacePrompt(null);
    setAttachFilesPrompt(null);
    setRemoveAttachedFilePrompt(null);
    setDeleteUploadedFilePrompt(null);
    setDeleteGeneratedFilePrompt(null);
    setEnableLiteratureSearchPrompt(null);
    setDisableLiteratureSearchPrompt(null);
    setStatus("");
    setIsSettingsPanelOpen(false);
    setIsChangePasswordOpen(false);
    setIsAboutOpen(false);
    setIsRegenerateConfirmOpen(false);
    setShowLogin(true);
    setWorkspaceData((current) => ({
      ...current,
      generated_documents: [],
      uploaded_documents: [],
      manuscript: [],
      ref_list: [],
      concept_maps: [],
      attached_files: [],
    }));
  }

  async function openGeneratedDocument(document) {
    const selectedFile = {
      ...document,
      file_name: document.file_name ?? document.name ?? "",
    };
    setGeneratedFile(selectedFile);
    setIsLiteratureSearchEnabled(false);
    setLiteratureCollectionName("");
    setFileName(selectedFile.file_name);
    setGeneratedContent("");
    setCurrentWritingSection("");
    setCurrentGenerationJobId("");
    setSelectedParagraph(null);

    if (!document.id) {
      setWorkspaceData((current) => ({ ...current, manuscript: [], ref_list: [], concept_maps: [], attached_files: [] }));
      setIsLiteratureSearchEnabled(false);
      setLiteratureCollectionName("");
      return;
    }

    setStatus("Loading manuscript...");
    try {
      const ownerQuery = authOwnerQuery(authSession);
      const queryString = ownerQuery ? `?${ownerQuery}` : "";
      const payload = await getJSON(`/api/generated-files/${document.id}/manuscript${queryString}`);
      const loadedFile = payload.generated_file ?? selectedFile;
      setGeneratedFile(loadedFile);
      setIsLiteratureSearchEnabled(Boolean(payload.literature_search?.collection_name));
      setLiteratureCollectionName(payload.literature_search?.collection_name ?? "");
      setFileName(loadedFile.file_name ?? selectedFile.file_name);
      const attachedDocuments = normalizeUploadedDocuments(payload.attached_files ?? []);
      setWorkspaceData((current) => ({
        ...current,
        manuscript: payload.manuscript ?? [],
        ref_list: normalizeReferenceList(payload.ref_list),
        concept_maps: [],
        attached_files: attachedDocuments,
        generated_documents: (current.generated_documents ?? []).map((document) =>
          String(document.id) === String(loadedFile.id)
            ? {
                ...document,
                ...generatedFileToDocument(loadedFile),
                attached_documents: attachedDocuments,
                attached_documents_count: attachedDocuments.length,
              }
            : document,
        ),
      }));
      setOutline(payload.outline ?? "");
      setOutlineMode("outline");
      setUseExample(false);
      outlineBeforeExample.current = "";
      setStatus(payload.message || "Manuscript loaded");
    } catch (error) {
      setWorkspaceData((current) => ({ ...current, manuscript: [], ref_list: [], concept_maps: [], attached_files: [] }));
      setStatus(error.message);
    }
  }

  async function openConceptMap() {
    if (!generatedFile?.id) {
      setStatus("Select a generated file before opening the concept map.");
      return;
    }

    setIsConceptMapOpen(true);
    setStatus("Loading concept map...");
    try {
      const ownerQuery = authOwnerQuery(authSession);
      const queryString = ownerQuery ? `?${ownerQuery}` : "";
      const payload = await getJSON(`/api/generated-files/${generatedFile.id}/concept-map${queryString}`);
      setWorkspaceData((current) => ({
        ...current,
        concept_maps: payload.concept_maps ?? [],
      }));
      setStatus(payload.message || "Concept map loaded");
    } catch (error) {
      setStatus(error.message);
    }
  }

  async function configureLiteratureSearch(checked) {
    if (!checked) {
      if (!generatedFile?.id) {
        setStatus("Select a generated file before disabling Literature Search.");
        return;
      }

      if (!isLiteratureSearchEnabled && !literatureCollectionName) {
        setStatus("Literature Search is already disabled for this file.");
        return;
      }

      setDisableLiteratureSearchPrompt(generatedFile);
      return;
    }

    if (!generatedFile?.id) {
      setStatus("Save this file before enabling Literature Search.");
      return;
    }

    setEnableLiteratureSearchPrompt(generatedFile);
  }

  function cancelEnableLiteratureSearch() {
    setEnableLiteratureSearchPrompt(null);
    setStatus("Literature Search is still disabled.");
  }

  async function confirmEnableLiteratureSearch() {
    const targetFile = enableLiteratureSearchPrompt;
    if (!targetFile?.id) {
      setEnableLiteratureSearchPrompt(null);
      setStatus("Save this file before enabling Literature Search.");
      return;
    }

    setEnableLiteratureSearchPrompt(null);
    const wasLiteratureSearchEnabled = isLiteratureSearchEnabled;
    const previousLiteratureCollectionName = literatureCollectionName;
    setIsConfiguringLiteratureSearch(true);
    setStatus("Setting up Literature Search...");
    try {
      const payload = await postJSON(`/api/generated-files/${targetFile.id}/literature-search`, {
        email: authSession?.user?.email ?? null,
        session: authSession?.user?.email ? null : (authSession?.session ?? null),
      });
      const updatedFile = payload.generated_file ?? {
        ...targetFile,
        ai_architecture: "rag",
      };
      setGeneratedFile(updatedFile);
      setIsLiteratureSearchEnabled(true);
      setLiteratureCollectionName(payload.collection_name ?? payload.literature_search?.collection_name ?? "");
      setGeneratedContent("");
      setCurrentWritingSection("");
      setCurrentGenerationJobId("");
      setSelectedParagraph(null);
      setWorkspaceData((current) => {
        const generatedDocuments = current.generated_documents ?? [];
        return {
          ...current,
          manuscript: payload.manuscript ?? current.manuscript,
          ref_list: normalizeReferenceList(payload.ref_list ?? current.ref_list),
          concept_maps: [],
          generated_documents: generatedDocuments.map((document) =>
            String(document.id) === String(updatedFile.id)
              ? {
                  ...document,
                  ai_architecture: updatedFile.ai_architecture,
                  status: updatedFile.status ?? document.status,
                  date: formatDocumentDate(updatedFile.update_date ?? document.update_date ?? document.date),
                  last_modified: formatDocumentDate(updatedFile.update_date ?? document.update_date ?? document.date),
                }
              : document,
          ),
        };
      });
      setStatus(payload.message || "Literature Search is enabled for this file.");
    } catch (error) {
      setIsLiteratureSearchEnabled(wasLiteratureSearchEnabled);
      setLiteratureCollectionName(previousLiteratureCollectionName);
      setStatus(error.message);
    } finally {
      setIsConfiguringLiteratureSearch(false);
    }
  }

  function cancelDisableLiteratureSearch() {
    setDisableLiteratureSearchPrompt(null);
    setStatus("Literature Search is still enabled.");
  }

  async function confirmDisableLiteratureSearch() {
    const targetFile = disableLiteratureSearchPrompt;
    if (!targetFile?.id) {
      setDisableLiteratureSearchPrompt(null);
      setStatus("Select a generated file before disabling Literature Search.");
      return;
    }

    setDisableLiteratureSearchPrompt(null);
    setIsConfiguringLiteratureSearch(true);
    setStatus("Disabling Literature Search...");
    try {
      const ownerQuery = authOwnerQuery(authSession);
      const queryString = ownerQuery ? `?${ownerQuery}` : "";
      const payload = await deleteJSON(`/api/generated-files/${targetFile.id}/literature-search${queryString}`);
      const updatedFile = payload.generated_file ?? generatedFile;
      setGeneratedFile(updatedFile);
      setIsLiteratureSearchEnabled(false);
      setLiteratureCollectionName("");
      setGeneratedContent("");
      setCurrentWritingSection("");
      setCurrentGenerationJobId("");
      setSelectedParagraph(null);
      setWorkspaceData((current) => ({
        ...current,
        manuscript: payload.manuscript ?? current.manuscript,
        ref_list: normalizeReferenceList(payload.ref_list ?? current.ref_list),
        concept_maps: [],
        attached_files: normalizeUploadedDocuments(payload.attached_files ?? current.attached_files),
        generated_documents: (current.generated_documents ?? []).map((document) =>
          String(document.id) === String(updatedFile.id)
            ? {
                ...document,
                ai_architecture: updatedFile.ai_architecture,
                status: updatedFile.status ?? document.status,
                date: formatDocumentDate(updatedFile.update_date ?? document.update_date ?? document.date),
              }
            : document,
        ),
      }));
      setStatus(payload.message || "Literature Search disabled for this file.");
    } catch (error) {
      setStatus(error.message);
    } finally {
      setIsConfiguringLiteratureSearch(false);
    }
  }

  async function saveSettings(draft) {
    if (!authSession?.user?.email || !authSession?.session || !authSession?.settings?.id) {
      const nextSettings = {
        ...(aiSettings ?? {}),
        ...draft,
      };
      setAiSettings(nextSettings);
      setAuthSession((current) => {
        if (!current) return current;
        const nextSession = {
          ...current,
          settings: {
            ...(current.settings ?? {}),
            ...nextSettings,
          },
          llm_options: llmOptions,
        };
        saveStoredAuthSession(nextSession);
        return nextSession;
      });
      setIsSettingsPanelOpen(false);
      setStatus("Settings updated for this session");
      return;
    }

    setIsSavingSettings(true);
    setStatus("Saving settings...");
    try {
      const email = encodeURIComponent(authSession.user.email);
      const session = encodeURIComponent(authSession.session);
      const payload = await patchJSON(`/api/settings/${authSession.settings.id}?email=${email}&session=${session}`, draft);
      setAiSettings(payload.settings);
      setLlmOptions(payload.llm_options ?? llmOptions);
      setAuthSession((current) => ({
        ...current,
        settings: payload.settings,
        llm_options: payload.llm_options ?? current?.llm_options ?? llmOptions,
      }));
      saveStoredAuthSession({
        ...authSession,
        settings: payload.settings,
        llm_options: payload.llm_options ?? authSession.llm_options ?? llmOptions,
      });
      setIsSettingsPanelOpen(false);
      setStatus("Settings saved");
    } catch (error) {
      setStatus(error.message);
    } finally {
      setIsSavingSettings(false);
    }
  }

  async function saveGeneratedFile() {
    const isGuest = authSession?.status === "anonymous";
    const isSignedIn = Boolean(authSession?.user?.email && authSession?.settings?.id);
    if (!authSession?.session || (!isGuest && !isSignedIn)) {
      setStatus("Log in or continue as guest before saving this file.");
      return;
    }

    const trimmedFileName = fileName.trim();
    if (!trimmedFileName) {
      setStatus("Enter a file name before saving.");
      return;
    }

    setIsSavingFile(true);
    setStatus("Saving file...");
    try {
      const wasCreatingFile = !generatedFile?.id;
      const payload = generatedFile?.id
        ? await patchJSON(`/api/generated-files/${generatedFile.id}`, {
            file_name: trimmedFileName,
          })
        : await postJSON("/api/generated-files", {
            email: authSession.user?.email ?? null,
            session: authSession.session,
            settings_id: authSession.settings?.id ?? null,
            file_name: trimmedFileName,
            ai_architecture: "base",
          });

      const savedFile = payload.generated_file;
      setGeneratedFile(savedFile);
      setIsLiteratureSearchEnabled(wasCreatingFile ? false : isLiteratureSearchEnabled);
      if (wasCreatingFile || !isLiteratureSearchEnabled) {
        setLiteratureCollectionName("");
      }
      setFileName(savedFile.file_name ?? trimmedFileName);
      setWorkspaceData((current) => {
        const generatedDocuments = current.generated_documents ?? [];
        const previousDocument = generatedDocuments.find((document) => String(document.id) === String(savedFile.id));
        const savedDocument = generatedFileToDocument({ ...(previousDocument ?? {}), ...savedFile });
        const withoutSavedDocument = generatedDocuments.filter((document) => String(document.id) !== String(savedDocument.id));
        return {
          ...current,
          generated_documents: [savedDocument, ...withoutSavedDocument],
          attached_files: wasCreatingFile ? [] : current.attached_files,
        };
      });
      setStatus("File saved");
    } catch (error) {
      setStatus(error.message);
    } finally {
      setIsSavingFile(false);
    }
  }

  async function uploadDocuments(files, replace = false) {
    const selectedFiles = Array.isArray(files) ? files : files ? [files] : [];
    if (!selectedFiles.length) return true;

    const ownerQuery = authOwnerQuery(authSession);
    if (!ownerQuery) {
      setStatus("Log in or continue as guest before uploading documents.");
      return false;
    }

    const formData = new FormData();
    selectedFiles.forEach((file) => formData.append("files", file));
    if (authSession?.user?.email) {
      formData.append("email", authSession.user.email);
    } else {
      formData.append("session", authSession.session);
    }
    formData.append("replace", replace ? "true" : "false");

    setIsUploadingDocuments(true);
    setStatus(replace ? "Replacing uploaded document..." : "Uploading documents...");
    try {
      const payload = await postForm("/api/uploaded-files", formData);
      setWorkspaceData((current) => ({
        ...current,
        uploaded_documents: normalizeUploadedDocuments(payload.uploaded_documents),
      }));
      setStatus(payload.message || "Documents uploaded successfully.");
      return true;
    } catch (error) {
      if (error.status === 409) {
        const duplicates = Array.isArray(error.detail?.duplicates) ? error.detail.duplicates : selectedFiles.map((file) => file.name);
        setUploadReplacePrompt({ files: selectedFiles, duplicates });
        setStatus(error.message);
        return true;
      }
      setStatus(error.message);
      return false;
    } finally {
      setIsUploadingDocuments(false);
    }
  }

  async function confirmUploadReplacement() {
    const files = uploadReplacePrompt?.files ?? [];
    setUploadReplacePrompt(null);
    await uploadDocuments(files, true);
  }

  function cancelUploadReplacement() {
    setUploadReplacePrompt(null);
    setStatus("Upload cancelled. Existing documents were not replaced.");
  }

  async function attachUploadedDocuments(documents, mode = "ask") {
    const selectedDocuments = Array.isArray(documents) ? documents : [];
    const uploadedFileIds = selectedDocuments.map((document) => Number(document.id)).filter(Number.isFinite);
    if (!uploadedFileIds.length) {
      setStatus("Select at least one uploaded document before attaching files.");
      return false;
    }

    if (!generatedFile?.id) {
      setStatus("Select a generated document before attaching uploaded files.");
      return false;
    }

    setIsAttachingUploadedDocuments(true);
    setStatus(mode === "replace" ? "Replacing attached files..." : "Attaching uploaded files...");
    try {
      const payload = await postJSON(`/api/generated-files/${generatedFile.id}/uploaded-files/attach`, {
        uploaded_file_ids: uploadedFileIds,
        email: authSession?.user?.email ?? null,
        session: authSession?.user?.email ? null : (authSession?.session ?? null),
        mode,
      });
      const updatedFile = payload.generated_file ?? generatedFile;
      setGeneratedFile(updatedFile);
      setWorkspaceData((current) => {
        const attachedDocuments = normalizeUploadedDocuments(payload.attached_files ?? current.attached_files);
        return {
          ...current,
          attached_files: attachedDocuments,
          generated_documents: (current.generated_documents ?? []).map((document) =>
            String(document.id) === String(updatedFile.id)
              ? {
                  ...document,
                  ai_architecture: updatedFile.ai_architecture,
                  date: formatDocumentDate(updatedFile.update_date ?? document.update_date ?? document.date),
                  last_modified: formatDocumentDate(updatedFile.update_date ?? document.update_date ?? document.date),
                  attached_documents: attachedDocuments,
                  attached_documents_count: attachedDocuments.length,
                }
              : document,
          ),
        };
      });
      setStatus(payload.message || "Uploaded documents attached to this generated document.");
      return true;
    } catch (error) {
      const detail = error.detail;
      if (error.status === 409 && detail?.reason === "already_attached") {
        setStatus(detail.message || "One or more selected files are already attached to this generated document.");
        return false;
      }
      if (error.status === 409 && detail?.reason === "existing_attachments") {
        setAttachFilesPrompt({
          documents: selectedDocuments,
          attachedFiles: Array.isArray(detail.attached_files) ? detail.attached_files : [],
          selectedFiles: Array.isArray(detail.selected_files) ? detail.selected_files : selectedDocuments.map((document) => document.name ?? document.file_name ?? "Untitled"),
        });
        setStatus(detail.message || "This generated document already has attached files.");
        return true;
      }

      setStatus(error.message);
      return false;
    } finally {
      setIsAttachingUploadedDocuments(false);
    }
  }

  async function appendUploadedFileAttachments() {
    const documents = attachFilesPrompt?.documents ?? [];
    setAttachFilesPrompt(null);
    await attachUploadedDocuments(documents, "append");
  }

  async function replaceUploadedFileAttachments() {
    const documents = attachFilesPrompt?.documents ?? [];
    setAttachFilesPrompt(null);
    await attachUploadedDocuments(documents, "replace");
  }

  function cancelUploadedFileAttachments() {
    setAttachFilesPrompt(null);
    setStatus("Attachment cancelled. Uploaded documents were not attached.");
  }

  async function removeAttachedFile(file) {
    if (!generatedFile?.id || !file?.id) {
      setStatus("Select a generated document before removing an attached file.");
      return;
    }

    setRemoveAttachedFilePrompt(file);
  }

  function cancelRemoveAttachedFile() {
    setRemoveAttachedFilePrompt(null);
    setStatus("Attached file was not removed.");
  }

  async function confirmRemoveAttachedFile() {
    const file = removeAttachedFilePrompt;
    if (!generatedFile?.id || !file?.id) {
      setRemoveAttachedFilePrompt(null);
      setStatus("Select a generated document before removing an attached file.");
      return;
    }

    setRemoveAttachedFilePrompt(null);
    setStatus("Removing attached file...");
    try {
      const ownerQuery = authOwnerQuery(authSession);
      const queryString = ownerQuery ? `?${ownerQuery}` : "";
      const payload = await deleteJSON(`/api/generated-files/${generatedFile.id}/uploaded-files/${file.id}/attach${queryString}`);
      const updatedFile = payload.generated_file ?? generatedFile;
      setGeneratedFile(updatedFile);
      const attachedDocuments = normalizeUploadedDocuments(payload.attached_files ?? []);
      setGeneratedContent("");
      setCurrentWritingSection("");
      setCurrentGenerationJobId("");
      setSelectedParagraph(null);
      setWorkspaceData((current) => ({
        ...current,
        manuscript: payload.manuscript ?? current.manuscript,
        ref_list: normalizeReferenceList(payload.ref_list ?? current.ref_list),
        concept_maps: [],
        attached_files: attachedDocuments,
        generated_documents: (current.generated_documents ?? []).map((document) =>
          String(document.id) === String(updatedFile.id)
            ? {
                ...document,
                ai_architecture: updatedFile.ai_architecture,
                status: updatedFile.status ?? document.status,
                date: formatDocumentDate(updatedFile.update_date ?? document.update_date ?? document.date),
                last_modified: formatDocumentDate(updatedFile.update_date ?? document.update_date ?? document.date),
                attached_documents: attachedDocuments,
                attached_documents_count: attachedDocuments.length,
              }
            : document,
        ),
      }));
      setStatus(payload.message || "Attached file removed.");
    } catch (error) {
      setStatus(error.message);
    }
  }

  function deleteUploadedDocument(document) {
    if (!document?.id) {
      setStatus("Select an uploaded document before deleting it.");
      return;
    }

    setDeleteUploadedFilePrompt(document);
  }

  function cancelDeleteUploadedDocument() {
    setDeleteUploadedFilePrompt(null);
    setStatus("Uploaded document was not deleted.");
  }

  async function confirmDeleteUploadedDocument() {
    const document = deleteUploadedFilePrompt;
    if (!document?.id) {
      setDeleteUploadedFilePrompt(null);
      setStatus("Select an uploaded document before deleting it.");
      return;
    }

    const ownerQuery = authOwnerQuery(authSession);
    if (!ownerQuery) {
      setDeleteUploadedFilePrompt(null);
      setStatus("Log in or continue as guest before deleting uploaded documents.");
      return;
    }

    setDeleteUploadedFilePrompt(null);
    setStatus("Deleting uploaded document...");
    try {
      const payload = await deleteJSON(`/api/uploaded-files/${document.id}?${ownerQuery}`);
      const affectedDocuments = Array.isArray(payload.affected_documents) ? payload.affected_documents : [];
      const affectedById = new Map(affectedDocuments.filter((affectedDocument) => affectedDocument?.generated_file?.id).map((affectedDocument) => [String(affectedDocument.generated_file.id), affectedDocument]));
      const selectedAffectedDocument = generatedFile?.id ? affectedById.get(String(generatedFile.id)) : null;

      if (selectedAffectedDocument?.generated_file) {
        const updatedFile = selectedAffectedDocument.generated_file;
        setGeneratedFile(updatedFile);
        setGeneratedContent("");
        setCurrentWritingSection("");
        setCurrentGenerationJobId("");
        setSelectedParagraph(null);
      }

      setWorkspaceData((current) => ({
        ...current,
        uploaded_documents: normalizeUploadedDocuments(payload.uploaded_documents ?? []),
        manuscript: selectedAffectedDocument?.manuscript ?? current.manuscript,
        ref_list: selectedAffectedDocument ? normalizeReferenceList(selectedAffectedDocument.ref_list) : current.ref_list,
        concept_maps: selectedAffectedDocument ? [] : current.concept_maps,
        attached_files: selectedAffectedDocument ? normalizeUploadedDocuments(selectedAffectedDocument.attached_files ?? []) : current.attached_files,
        generated_documents: (current.generated_documents ?? []).map((currentDocument) => {
          const affectedDocument = affectedById.get(String(currentDocument.id));
          const affectedFile = affectedDocument?.generated_file;
          if (!affectedFile) return currentDocument;

          return {
            ...currentDocument,
            name: affectedFile.file_name ?? currentDocument.name,
            file_name: affectedFile.file_name ?? currentDocument.file_name,
            ai_architecture: affectedFile.ai_architecture,
            status: affectedFile.status ?? currentDocument.status,
            date: formatDocumentDate(affectedFile.update_date ?? currentDocument.update_date ?? currentDocument.date),
            last_modified: formatDocumentDate(affectedFile.update_date ?? currentDocument.update_date ?? currentDocument.date),
            attached_documents: normalizeUploadedDocuments(affectedDocument.attached_files ?? []),
            attached_documents_count: Array.isArray(affectedDocument.attached_files) ? affectedDocument.attached_files.length : 0,
          };
        }),
      }));
      setStatus(payload.message || "Uploaded document deleted.");
    } catch (error) {
      setStatus(error.message);
    }
  }

  async function downloadGeneratedDocument(document, format = "md") {
    if (!document?.id) {
      setStatus("Select a generated document before downloading it.");
      return;
    }

    const downloadFormat = ["md", "docx", "latex"].includes(format) ? format : "md";
    const extension = downloadFormat === "latex" ? "zip" : downloadFormat;
    setStatus("Preparing generated document download...");
    try {
      const ownerQuery = authOwnerQuery(authSession);
      const params = new URLSearchParams(ownerQuery);
      params.set("format", downloadFormat);
      const fileTitle = document.file_name ?? document.name ?? "generated-document";
      const blob = await getBlob(`/api/generated-files/${document.id}/download?${params.toString()}`);
      downloadBlobFile(`${safeDownloadName(fileTitle)}.${extension}`, blob);
      setStatus("Generated document downloaded.");
    } catch (error) {
      setStatus(error.message);
    }
  }

  function deleteGeneratedDocument(document) {
    if (!document?.id) {
      setStatus("Select a generated document before removing it.");
      return;
    }

    setDeleteGeneratedFilePrompt(document);
  }

  function cancelDeleteGeneratedDocument() {
    setDeleteGeneratedFilePrompt(null);
    setStatus("Generated document was not removed.");
  }

  async function confirmDeleteGeneratedDocument() {
    const document = deleteGeneratedFilePrompt;
    if (!document?.id) {
      setDeleteGeneratedFilePrompt(null);
      setStatus("Select a generated document before removing it.");
      return;
    }

    const ownerQuery = authOwnerQuery(authSession);
    const queryString = ownerQuery ? `?${ownerQuery}` : "";

    setDeleteGeneratedFilePrompt(null);
    setStatus("Removing generated document...");
    try {
      const payload = await deleteJSON(`/api/generated-files/${document.id}${queryString}`);
      const removedSelectedDocument = String(generatedFile?.id) === String(document.id);
      if (removedSelectedDocument) {
        setGeneratedFile(null);
        setFileName("");
        setOutline("");
        setUseExample(false);
        setLiteratureCollectionName("");
        setIsLiteratureSearchEnabled(false);
        setGeneratedContent("");
        setCurrentWritingSection("");
        setCurrentGenerationJobId("");
        setSelectedParagraph(null);
        setIsConceptMapOpen(false);
      }

      setWorkspaceData((current) => ({
        ...current,
        generated_documents: normalizeGeneratedDocuments(payload.generated_documents ?? []),
        manuscript: removedSelectedDocument ? [] : current.manuscript,
        ref_list: removedSelectedDocument ? [] : current.ref_list,
        concept_maps: removedSelectedDocument ? [] : current.concept_maps,
        attached_files: removedSelectedDocument ? [] : current.attached_files,
      }));
      setStatus(payload.message || "Generated document removed.");
    } catch (error) {
      setStatus(error.message);
    }
  }

  if (showLogin) {
    return <LoginPage onContinue={enterWorkspace} />;
  }

  return (
    <div className={`app-window ${isSidebarCollapsed ? "sidebar-collapsed" : ""}`} data-view="workspace">
      <TopBar
        accountLabel={authSession?.user?.email ?? "Anonymous session"}
        isGuest={authSession?.status === "anonymous" || !authSession?.user?.email}
        onChangePassword={() => setIsChangePasswordOpen(true)}
        onHelp={() => setIsAboutOpen(true)}
        onLogout={logout}
      />
      <Sidebar
        generatedDocuments={workspaceData.generated_documents}
        selectedGeneratedDocumentId={generatedFile?.id}
        onGeneratedDocumentSelect={openGeneratedDocument}
        onGeneratedDocumentsExpand={() => setIsGeneratedDocumentsViewOpen(true)}
        onGeneratedDocumentDownload={downloadGeneratedDocument}
        onGeneratedDocumentDelete={deleteGeneratedDocument}
        isLoadingGeneratedDocuments={isLoadingGeneratedDocuments}
        uploadedDocuments={workspaceData.uploaded_documents}
        isLoadingUploadedDocuments={isLoadingUploadedDocuments}
        onUploadedDocumentsUpload={uploadDocuments}
        onUploadedDocumentDelete={deleteUploadedDocument}
        isUploadingDocuments={isUploadingDocuments}
        onAttachUploadedDocuments={attachUploadedDocuments}
        isAttachingUploadedDocuments={isAttachingUploadedDocuments}
        health={systemHealth}
        isHealthLoading={isHealthLoading}
        isCollapsed={isSidebarCollapsed}
        onToggleCollapse={() => setIsSidebarCollapsed((current) => !current)}
      />
      <main className={`workspace ${selectedParagraph?.text ? "" : "workspace-compact-action-strip"}`.trim()}>
        <WorkspaceHeader fileName={fileName} setFileName={setFileName} onSave={saveGeneratedFile} onNewDocument={newDocument} isSaving={isSavingFile} settings={aiSettings} onOpenSettings={() => setIsSettingsPanelOpen(true)} />
        <OutlinePanel
          mode={outlineMode}
          setMode={setOutlineMode}
          query={query}
          setQuery={setQuery}
          referenceDocument={referenceDocument}
          setReferenceDocument={setReferenceDocument}
          outline={outline}
          setOutline={updateOutlineFromEditor}
          useExample={useExample}
          setUseExample={setUseExampleOutline}
          onGenerate={generateOutline}
          onFormat={formatOutline}
          onRun={runStructuredOutline}
          onRegenerate={regenerateStructuredOutline}
          onPause={pauseStructuredOutline}
          onDownload={(format) => downloadGeneratedDocument(generatedFile, format)}
          isRunning={isSavingOutline}
          status={status}
          hasSelectedFile={Boolean(generatedFile?.id)}
          hasGeneratedContent={hasManuscriptContent(workspaceData.manuscript, generatedContent)}
          resetSignal={workspaceResetVersion}
        />
        <ActionStrip
          action={action}
          setAction={setAction}
          onWrite={writeContent}
          isWriting={isWriting}
          onOpenConceptMap={openConceptMap}
          hasSelectedFile={Boolean(generatedFile?.id)}
          isLiteratureSearchEnabled={isLiteratureSearchEnabled}
          isConfiguringLiteratureSearch={isConfiguringLiteratureSearch}
          onLiteratureSearchChange={configureLiteratureSearch}
          attachedFiles={workspaceData.attached_files}
          onRemoveAttachedFile={removeAttachedFile}
          hasSelectedParagraphText={Boolean(selectedParagraph?.text)}
        />
        <Manuscript manuscript={workspaceData.manuscript} refList={workspaceData.ref_list} generatedContent={generatedContent} isGenerating={isSavingOutline} currentWritingSection={currentWritingSection} selectedParagraphId={selectedParagraph?.id ?? ""} updatingParagraphId={updatingParagraphId} onParagraphSelectionChange={setSelectedParagraph} />
      </main>
      <SettingsPanel settings={aiSettings} modelOptions={llmOptions} isOpen={isSettingsPanelOpen} isSaving={isSavingSettings} onClose={() => setIsSettingsPanelOpen(false)} onSave={saveSettings} />
      {isChangePasswordOpen && authSession?.user?.email ? (
        <ChangePasswordDialog
          email={authSession.user.email}
          onClose={() => setIsChangePasswordOpen(false)}
          onChanged={(payload) => {
            setIsChangePasswordOpen(false);
            setStatus(payload.message ?? "Password changed successfully.");
          }}
        />
      ) : null}
      {isGeneratedDocumentsViewOpen ? (
        <GeneratedDocumentsView
          documents={workspaceData.generated_documents}
          selectedDocumentId={generatedFile?.id}
          isLoading={isLoadingGeneratedDocuments}
          onClose={() => setIsGeneratedDocumentsViewOpen(false)}
          onSelect={(document) => {
            setIsGeneratedDocumentsViewOpen(false);
            openGeneratedDocument(document);
          }}
          onDownload={downloadGeneratedDocument}
          onRemove={deleteGeneratedDocument}
        />
      ) : null}
      <ConfirmDialog
        isOpen={isRegenerateConfirmOpen}
        title="Regenerate manuscript?"
        dialogId="regenerate-confirm"
        icon={<AlertTriangle size={19} />}
        onClose={() => setIsRegenerateConfirmOpen(false)}
        actions={[
          { label: "Cancel", onClick: () => setIsRegenerateConfirmOpen(false), autoFocus: true },
          { label: "Regenerate", onClick: confirmRegenerateStructuredOutline, variant: "danger", icon: <RefreshCw size={15} /> },
        ]}
      >
        <p>This will start from the beginning of the outline and replace any manuscript content already generated for this file.</p>
      </ConfirmDialog>
      <ConfirmDialog
        isOpen={Boolean(disableLiteratureSearchPrompt)}
        title="Disable Literature Search?"
        dialogId="disable-literature-search-confirm"
        icon={<AlertTriangle size={19} />}
        onClose={cancelDisableLiteratureSearch}
        actions={[
          { label: "Cancel", onClick: cancelDisableLiteratureSearch, autoFocus: true },
          { label: "Disable and reset", onClick: confirmDisableLiteratureSearch, variant: "danger", icon: <RefreshCw size={15} /> },
        ]}
      >
        <p>Disabling Literature Search will remove the literature collection from this generated document and reset the manuscript content. Your saved outline will stay in place.</p>
      </ConfirmDialog>
      <ConfirmDialog
        isOpen={Boolean(enableLiteratureSearchPrompt)}
        title="Enable Literature Search?"
        dialogId="enable-literature-search-confirm"
        icon={<AlertTriangle size={19} />}
        onClose={cancelEnableLiteratureSearch}
        actions={[
          { label: "Cancel", onClick: cancelEnableLiteratureSearch, autoFocus: true },
          { label: "Enable and reset", onClick: confirmEnableLiteratureSearch, variant: "danger", icon: <RefreshCw size={15} /> },
        ]}
      >
        <p>Enabling Literature Search will change the generation context and reset the manuscript content for this generated document. Your saved outline will stay in place.</p>
      </ConfirmDialog>
      <ConfirmDialog
        isOpen={Boolean(uploadReplacePrompt)}
        title="Replace uploaded document?"
        dialogId="upload-replace-confirm"
        icon={<AlertTriangle size={19} />}
        onClose={cancelUploadReplacement}
        actions={[
          { label: "Cancel", onClick: cancelUploadReplacement, autoFocus: true },
          { label: "Replace", onClick: confirmUploadReplacement, variant: "danger", icon: <Upload size={15} /> },
        ]}
      >
        <p>
          <strong>{uploadReplacePrompt?.duplicates?.length ? uploadReplacePrompt.duplicates.join(", ") : "The selected document"}</strong> already exists for this account or session. Replacing will update the saved file and refresh its upload date.
        </p>
      </ConfirmDialog>
      <ConfirmDialog
        isOpen={Boolean(attachFilesPrompt)}
        title="Attach selected files?"
        dialogId="attach-files-confirm"
        icon={<FilePlus2 size={19} />}
        onClose={cancelUploadedFileAttachments}
        actions={[
          { label: "Cancel", onClick: cancelUploadedFileAttachments },
          { label: "Add to existing", onClick: appendUploadedFileAttachments, variant: "primary", icon: <GitMerge size={15} />, autoFocus: true },
          { label: "Replace existing", onClick: replaceUploadedFileAttachments, variant: "danger", icon: <RefreshCw size={15} /> },
        ]}
      >
        <p>This generated document already has attached files. Add the selected files to that set, or replace the current set?</p>
        <dl>
          <div>
            <dt>Already attached</dt>
            <dd>{attachFilesPrompt?.attachedFiles?.length ? attachFilesPrompt.attachedFiles.join(", ") : "None"}</dd>
          </div>
          <div>
            <dt>Selected</dt>
            <dd>{attachFilesPrompt?.selectedFiles?.length ? attachFilesPrompt.selectedFiles.join(", ") : "None"}</dd>
          </div>
        </dl>
      </ConfirmDialog>
      <ConfirmDialog
        isOpen={Boolean(removeAttachedFilePrompt)}
        title="Remove attached file?"
        dialogId="remove-attached-file-confirm"
        icon={<AlertTriangle size={19} />}
        onClose={cancelRemoveAttachedFile}
        actions={[
          { label: "Cancel", onClick: cancelRemoveAttachedFile, autoFocus: true },
          { label: "Remove and reset", onClick: confirmRemoveAttachedFile, variant: "danger", icon: <Trash2 size={15} /> },
        ]}
      >
        <p>
          Removing <strong>{removeAttachedFilePrompt?.name ?? removeAttachedFilePrompt?.file_name ?? "this attached file"}</strong> will reset the manuscript content for this generated document. Your saved outline will stay in place.
        </p>
      </ConfirmDialog>
      <ConfirmDialog
        isOpen={Boolean(deleteUploadedFilePrompt)}
        title="Delete uploaded document?"
        dialogId="delete-uploaded-file-confirm"
        icon={<AlertTriangle size={19} />}
        onClose={cancelDeleteUploadedDocument}
        actions={[
          { label: "Cancel", onClick: cancelDeleteUploadedDocument, autoFocus: true },
          { label: "Delete and reset", onClick: confirmDeleteUploadedDocument, variant: "danger", icon: <Trash2 size={15} /> },
        ]}
      >
        <p>
          Deleting <strong>{deleteUploadedFilePrompt?.name ?? deleteUploadedFilePrompt?.file_name ?? "this uploaded document"}</strong> will remove it from your uploaded documents and reset any generated document that had it attached.
        </p>
      </ConfirmDialog>
      <ConfirmDialog
        isOpen={Boolean(deleteGeneratedFilePrompt)}
        title="Remove generated document?"
        dialogId="delete-generated-file-confirm"
        icon={<AlertTriangle size={19} />}
        onClose={cancelDeleteGeneratedDocument}
        actions={[
          { label: "Cancel", onClick: cancelDeleteGeneratedDocument, autoFocus: true },
          { label: "Remove", onClick: confirmDeleteGeneratedDocument, variant: "danger", icon: <Trash2 size={15} /> },
        ]}
      >
        <p>
          Removing <strong>{deleteGeneratedFilePrompt?.name ?? deleteGeneratedFilePrompt?.file_name ?? "this generated document"}</strong> will hide it from the generated documents list. Any active reference collections for it will also be disabled.
        </p>
      </ConfirmDialog>
      {isAboutOpen ? <AboutPage onClose={() => setIsAboutOpen(false)} /> : null}
      {isConceptMapOpen ? <ConceptMapPanel conceptMaps={workspaceData.concept_maps} fileName={fileName} onClose={() => setIsConceptMapOpen(false)} /> : null}
    </div>
  );
}
