import { useEffect, useRef, useState } from "react";
import { getJSON, patchJSON, postJSON } from "../api/client";
import { AboutPage } from "./AboutPage";
import { ActionStrip } from "./ActionStrip";
import { Manuscript } from "./Manuscript";
import { LoginPage } from "./LoginPage";
import { OutlinePanel } from "./OutlinePanel";
import { Sidebar } from "./Sidebar";
import { SettingsPanel } from "./SettingsPanel";
import { TopBar } from "./TopBar";
import { WorkspaceHeader } from "./WorkspaceHeader";

function formatDocumentDate(value) {
  if (!value) return "";

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;

  return date.toLocaleString();
}

function generatedFileToDocument(file = {}) {
  const name = file.name ?? file.file_name ?? "Untitled";

  return {
    ...file,
    id: file.id,
    name,
    file_name: file.file_name ?? name,
    date: formatDocumentDate(file.date ?? file.update_date ?? file.create_date),
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

function wait(milliseconds) {
  return new Promise((resolve) => {
    window.setTimeout(resolve, milliseconds);
  });
}

function generationStatusMessage(job = {}) {
  if (job.status === "completed") return job.message || "Content generation completed.";
  if (job.status === "error") return job.error || job.message || "Content generation stopped.";

  const completed = Number(job.completed_sections ?? 0);
  const total = Number(job.total_sections ?? 0);
  if (job.current_section && total > 0) {
    return `Writing section ${Math.min(completed + 1, total)} of ${total}: ${job.current_section}`;
  }

  return job.message || "Preparing content generation...";
}

export function App() {
  const outlineBeforeExample = useRef("");
  const [showLogin, setShowLogin] = useState(true);
  const [authSession, setAuthSession] = useState(null);
  const [aiSettings, setAiSettings] = useState(null);
  const [llmOptions, setLlmOptions] = useState([]);
  const [isSettingsPanelOpen, setIsSettingsPanelOpen] = useState(false);
  const [isAboutOpen, setIsAboutOpen] = useState(false);
  const [isSavingSettings, setIsSavingSettings] = useState(false);
  const [isSavingOutline, setIsSavingOutline] = useState(false);
  const [isSavingFile, setIsSavingFile] = useState(false);
  const [generatedFile, setGeneratedFile] = useState(null);
  const [fileName, setFileName] = useState("");
  const [query, setQuery] = useState("");
  const [referenceDocument, setReferenceDocument] = useState(null);
  const [outlineMode, setOutlineMode] = useState("outline");
  const [outline, setOutline] = useState("");
  const [useExample, setUseExample] = useState(false);
  const [action, setAction] = useState("Expand");
  const [status, setStatus] = useState("");
  const [generatedContent, setGeneratedContent] = useState("");
  const [isWriting, setIsWriting] = useState(false);
  const [workspaceData, setWorkspaceData] = useState({
    manuscript: [],
    generated_documents: [],
    uploaded_documents: [],
  });

  useEffect(() => {
    let isMounted = true;

    async function loadWorkspaceData() {
      try {
        const payload = await getJSON("/api/workspace");
        if (!isMounted) return;
        setWorkspaceData((current) => ({
          ...current,
          manuscript: current.manuscript?.length ? current.manuscript : (payload.manuscript ?? []),
          generated_documents: current.generated_documents?.length
            ? current.generated_documents
            : (payload.generated_documents ?? []),
          uploaded_documents: current.uploaded_documents?.length
            ? current.uploaded_documents
            : (payload.uploaded_documents ?? []),
        }));
        setOutline(payload.outline_template ?? "");
      } catch (error) {
        if (isMounted) {
          setStatus(error.message);
        }
      }
    }

    loadWorkspaceData();

    return () => {
      isMounted = false;
    };
  }, []);

  useEffect(() => {
    if (!authSession?.user?.email) return undefined;

    let isMounted = true;

    async function loadWorkspaceSessionData() {
      try {
        const email = encodeURIComponent(authSession.user.email);
        const session = encodeURIComponent(authSession.session);
        const settingsId = authSession.settings?.id;
        const [generatedPayload, uploadedPayload, settingsPayload] = await Promise.all([
          getJSON(`/api/generated-files?email=${email}`),
          getJSON(`/api/uploaded-files?email=${email}`),
          settingsId ? getJSON(`/api/settings/${settingsId}?email=${email}&session=${session}`) : Promise.resolve({}),
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

  async function writeContent() {
    if (!generatedFile?.id) {
      setStatus("Save this file before starting content generation.");
      return;
    }

    setIsWriting(true);
    setStatus("Writing content...");
    try {
      const payload = await postJSON("/api/ai/content", {
        architecture_type: "base",
        current_section: outline,
        content_pre: generatedContent,
        content_specific_instructions: action,
        model_name: aiSettings?.llm,
        temperature: Number(aiSettings?.temperature ?? 0),
        instructions: aiSettings?.instructions ?? "",
      });
      const content = payload.result?.content ?? "";
      setGeneratedContent(content);
      setStatus("Content written");
    } catch (error) {
      setStatus(error.message);
    } finally {
      setIsWriting(false);
    }
  }

  async function runStructuredOutline() {
    if (!generatedFile?.id) {
      setStatus("Save this file before running the structured outline.");
      return;
    }

    if (!outline.trim()) {
      setStatus("Add a structured outline before running it.");
      return;
    }

    setIsSavingOutline(true);
    setGeneratedContent("");
    setStatus("Saving structured outline...");
    try {
      const payload = await postJSON(`/api/generated-files/${generatedFile.id}/generate`, {
        outline,
        email: authSession?.user?.email ?? null,
        session: authSession?.user?.email ? null : (authSession?.session ?? null),
        architecture_type: generatedFile.ai_architecture ?? "base",
        model_name: aiSettings?.llm,
        temperature: Number(aiSettings?.temperature ?? 0),
        instructions: aiSettings?.instructions ?? "",
      });
      let job = payload.job;
      const savedFile = job?.generated_file ?? generatedFile;
      setGeneratedFile(savedFile);
      setWorkspaceData((current) => {
        const generatedDocuments = current.generated_documents ?? [];
        return {
          ...current,
          manuscript: job?.manuscript ?? current.manuscript,
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
      setStatus(generationStatusMessage(job));

      while (job?.status === "queued" || job?.status === "running") {
        await wait(1200);
        const jobPayload = await getJSON(`/api/generation-jobs/${job.id}`);
        job = jobPayload.job;
        setStatus(generationStatusMessage(job));
        setWorkspaceData((current) => {
          const generatedDocuments = current.generated_documents ?? [];
          return {
            ...current,
            manuscript: job?.manuscript ?? current.manuscript,
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

      if (job?.status === "error") {
        throw new Error(job.error || "Content generation stopped before it finished.");
      }

      if (job?.generated_file) {
        setGeneratedFile(job.generated_file);
      }
      setStatus(generationStatusMessage(job));
    } catch (error) {
      setStatus(error.message);
    } finally {
      setIsSavingOutline(false);
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
    setAiSettings(sessionPayload?.settings ?? null);
    setLlmOptions(sessionPayload?.llm_options ?? []);
    setShowLogin(false);
  }

  function logout() {
    setAuthSession(null);
    setAiSettings(null);
    setLlmOptions([]);
    setGeneratedFile(null);
    setFileName("");
    setReferenceDocument(null);
    setGeneratedContent("");
    setIsSavingFile(false);
    setIsSavingOutline(false);
    setStatus("");
    setIsSettingsPanelOpen(false);
    setIsAboutOpen(false);
    setShowLogin(true);
    setWorkspaceData((current) => ({
      ...current,
      generated_documents: [],
      uploaded_documents: [],
      manuscript: [],
    }));
  }

  async function openGeneratedDocument(document) {
    const selectedFile = {
      ...document,
      file_name: document.file_name ?? document.name ?? "",
    };
    setGeneratedFile(selectedFile);
    setFileName(selectedFile.file_name);
    setGeneratedContent("");

    if (!document.id) {
      setWorkspaceData((current) => ({ ...current, manuscript: [] }));
      return;
    }

    setStatus("Loading manuscript...");
    try {
      const params = new URLSearchParams();
      if (authSession?.user?.email) params.set("email", authSession.user.email);
      else if (authSession?.session) params.set("session", authSession.session);
      const queryString = params.toString() ? `?${params.toString()}` : "";
      const payload = await getJSON(`/api/generated-files/${document.id}/manuscript${queryString}`);
      const loadedFile = payload.generated_file ?? selectedFile;
      setGeneratedFile(loadedFile);
      setFileName(loadedFile.file_name ?? selectedFile.file_name);
      setWorkspaceData((current) => ({
        ...current,
        manuscript: payload.manuscript ?? [],
      }));
      setStatus(payload.message || "Manuscript loaded");
    } catch (error) {
      setWorkspaceData((current) => ({ ...current, manuscript: [] }));
      setStatus(error.message);
    }
  }

  async function saveSettings(draft) {
    if (!authSession?.user?.email || !authSession?.session || !authSession?.settings?.id) {
      setAiSettings((current) => ({
        ...(current ?? {}),
        ...draft,
      }));
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
      }));
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
      setFileName(savedFile.file_name ?? trimmedFileName);
      setWorkspaceData((current) => {
        const savedDocument = generatedFileToDocument(savedFile);
        const generatedDocuments = current.generated_documents ?? [];
        const withoutSavedDocument = generatedDocuments.filter((document) => String(document.id) !== String(savedDocument.id));
        return {
          ...current,
          generated_documents: [savedDocument, ...withoutSavedDocument],
        };
      });
      setStatus("File saved");
    } catch (error) {
      setStatus(error.message);
    } finally {
      setIsSavingFile(false);
    }
  }

  if (showLogin) {
    return <LoginPage onContinue={enterWorkspace} />;
  }

  return (
    <div className="app-window" data-view="workspace">
      <TopBar
        accountLabel={authSession?.user?.email ?? "Anonymous session"}
        isGuest={authSession?.status === "anonymous" || !authSession?.user?.email}
        onHelp={() => setIsAboutOpen(true)}
        onLogout={logout}
      />
      <Sidebar
        generatedDocuments={workspaceData.generated_documents}
        selectedGeneratedDocumentId={generatedFile?.id}
        onGeneratedDocumentSelect={openGeneratedDocument}
        uploadedDocuments={workspaceData.uploaded_documents}
      />
      <main className="workspace">
        <WorkspaceHeader
          fileName={fileName}
          setFileName={setFileName}
          onSave={saveGeneratedFile}
          isSaving={isSavingFile}
          settings={aiSettings}
          onOpenSettings={() => setIsSettingsPanelOpen(true)}
        />
        <OutlinePanel
          mode={outlineMode}
          setMode={setOutlineMode}
          query={query}
          setQuery={setQuery}
          referenceDocument={referenceDocument}
          setReferenceDocument={setReferenceDocument}
          outline={outline}
          setOutline={setOutline}
          useExample={useExample}
          setUseExample={setUseExampleOutline}
          onGenerate={generateOutline}
          onFormat={formatOutline}
          onRun={runStructuredOutline}
          isRunning={isSavingOutline}
          status={status}
        />
        <ActionStrip action={action} setAction={setAction} onWrite={writeContent} isWriting={isWriting} />
        <Manuscript manuscript={workspaceData.manuscript} generatedContent={generatedContent} />
      </main>
      <SettingsPanel
        settings={aiSettings}
        modelOptions={llmOptions}
        isOpen={isSettingsPanelOpen}
        isSaving={isSavingSettings}
        onClose={() => setIsSettingsPanelOpen(false)}
        onSave={saveSettings}
      />
      {isAboutOpen ? <AboutPage onClose={() => setIsAboutOpen(false)} /> : null}
    </div>
  );
}
