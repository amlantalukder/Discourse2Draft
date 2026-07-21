import { useEffect, useState } from "react";
import { getJSON, postJSON } from "../api/client";
import { AlertTriangle, ChevronDown, ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight, ChevronUp, RefreshCw, Search, Trash2, X } from "./FontAwesomeIcons";
import { ConfirmDialog } from "./ConfirmDialog";
import { IconButton } from "./IconButton";
import { StatusBar } from "./StatusBar";

const DEFAULT_FILTERS = {
  search: "",
  status: "ALL",
  dateFrom: "",
  dateTo: "",
  sortBy: "date",
  sortDir: "desc",
  page: 1,
  pageSize: 25,
};

const LOG_MESSAGE_PREVIEW_LENGTH = 420;
const LOG_MESSAGE_PREVIEW_LINES = 6;

function statusClass(status) {
  return String(status || "unknown").toLowerCase();
}

function maintainerQuery(authSession, filters) {
  const params = new URLSearchParams();
  params.set("email", authSession?.user?.email ?? "");
  params.set("session", authSession?.session ?? "");
  if (filters.search.trim()) params.set("search", filters.search.trim());
  if (filters.status && filters.status !== "ALL") params.set("status", filters.status);
  if (filters.dateFrom) params.set("date_from", filters.dateFrom);
  if (filters.dateTo) params.set("date_to", filters.dateTo);
  params.set("sort_by", filters.sortBy);
  params.set("sort_dir", filters.sortDir);
  params.set("page", String(filters.page));
  params.set("page_size", String(filters.pageSize));
  return params.toString();
}

export function MaintainerLogsPage({ authSession, onClose }) {
  const [filters, setFilters] = useState(DEFAULT_FILTERS);
  const [entries, setEntries] = useState([]);
  const [statuses, setStatuses] = useState([]);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [feedback, setFeedback] = useState({ message: "", tone: "info" });
  const [selectedLogIds, setSelectedLogIds] = useState(() => new Set());
  const [isClearConfirmOpen, setIsClearConfirmOpen] = useState(false);
  const [isClearing, setIsClearing] = useState(false);
  const [reloadToken, setReloadToken] = useState(0);
  const [expandedLogIds, setExpandedLogIds] = useState(() => new Set());
  const visibleLogIds = entries.map((entry) => String(entry.id));
  const areAllVisibleLogsSelected = visibleLogIds.length > 0 && visibleLogIds.every((id) => selectedLogIds.has(id));
  const showTopPagination = total > 10;
  const visibleStart = total && entries.length ? (filters.page - 1) * filters.pageSize + 1 : 0;
  const visibleEnd = total && entries.length ? visibleStart + entries.length - 1 : 0;

  useEffect(() => {
    function handleKeyDown(event) {
      if (event.key === "Escape") {
        onClose?.();
      }
    }

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [onClose]);

  useEffect(() => {
    let isMounted = true;

    async function loadLogs() {
      if (!authSession?.user?.email || !authSession?.session) {
        setFeedback({ message: "Maintainer session is missing. Log out and log in again.", tone: "error" });
        setEntries([]);
        setTotal(0);
        setTotalPages(1);
        return;
      }

      setIsLoading(true);
      setFeedback({ message: "", tone: "info" });
      try {
        const payload = await getJSON(`/api/maintainer/logs?${maintainerQuery(authSession, filters)}`);
        if (!isMounted) return;
        setEntries(payload.entries ?? []);
        setStatuses(payload.statuses ?? []);
        setTotal(Number(payload.total ?? 0));
        setTotalPages(Number(payload.total_pages ?? 1));
        const nextVisibleIds = new Set((payload.entries ?? []).map((entry) => String(entry.id)));
        setSelectedLogIds((current) => new Set([...current].filter((id) => nextVisibleIds.has(id))));
        setExpandedLogIds((current) => new Set([...current].filter((id) => nextVisibleIds.has(id))));
        if (Number(payload.page ?? filters.page) !== filters.page) {
          setFilters((current) => ({ ...current, page: Number(payload.page ?? current.page) }));
        }
      } catch (loadError) {
        if (!isMounted) return;
        setFeedback({ message: loadError.message, tone: "error" });
        setEntries([]);
        setTotal(0);
        setTotalPages(1);
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    loadLogs();
    return () => {
      isMounted = false;
    };
  }, [authSession, filters, reloadToken]);

  function updateFilter(field, value) {
    setFilters((current) => ({ ...current, [field]: value, page: 1 }));
  }

  function goToPage(page) {
    setFilters((current) => ({
      ...current,
      page: Math.max(1, Math.min(page, totalPages)),
    }));
  }

  function sortBy(field) {
    setFilters((current) => ({
      ...current,
      sortBy: field,
      sortDir: current.sortBy === field && current.sortDir === "asc" ? "desc" : "asc",
      page: 1,
    }));
  }

  function sortLabel(field) {
    if (filters.sortBy !== field) return "";
    return filters.sortDir === "asc" ? " ascending" : " descending";
  }

  function renderDateSortIcon() {
    const isDateSortActive = filters.sortBy === "date";
    const SortIcon = isDateSortActive && filters.sortDir === "asc" ? ChevronUp : ChevronDown;
    return <SortIcon className="maintainer-sort-icon" size={10} />;
  }

  function toggleVisibleLogs(checked) {
    setSelectedLogIds((current) => {
      const next = new Set(current);
      visibleLogIds.forEach((id) => {
        if (checked) {
          next.add(id);
        } else {
          next.delete(id);
        }
      });
      return next;
    });
  }

  function toggleLogSelection(entryId, checked) {
    const normalizedId = String(entryId);
    setSelectedLogIds((current) => {
      const next = new Set(current);
      if (checked) {
        next.add(normalizedId);
      } else {
        next.delete(normalizedId);
      }
      return next;
    });
  }

  function toggleLogMessage(entryId) {
    const normalizedId = String(entryId);
    setExpandedLogIds((current) => {
      const next = new Set(current);
      if (next.has(normalizedId)) {
        next.delete(normalizedId);
      } else {
        next.add(normalizedId);
      }
      return next;
    });
  }

  async function clearSelectedLogs() {
    if (!selectedLogIds.size || !authSession?.user?.email || !authSession?.session) return;

    setIsClearing(true);
    setFeedback({ message: "", tone: "info" });
    try {
      const payload = await postJSON("/api/maintainer/logs/clear", {
        email: authSession.user.email,
        session: authSession.session,
        entry_ids: [...selectedLogIds].map((id) => Number(id)).filter(Number.isFinite),
      });
      setSelectedLogIds(new Set());
      setIsClearConfirmOpen(false);
      setFeedback({ message: payload.message || "Selected log entries were cleared.", tone: "info" });
      setReloadToken((current) => current + 1);
    } catch (clearError) {
      setFeedback({ message: clearError.message, tone: "error" });
    } finally {
      setIsClearing(false);
    }
  }

  function renderLogMessage(entry) {
    const message = String(entry.message ?? "");
    const normalizedId = String(entry.id);
    const isLongMessage = message.length > LOG_MESSAGE_PREVIEW_LENGTH || message.split("\n").length > LOG_MESSAGE_PREVIEW_LINES;
    const isExpanded = expandedLogIds.has(normalizedId);
    const preview = isLongMessage && !isExpanded ? `${message.slice(0, LOG_MESSAGE_PREVIEW_LENGTH).trim()}...` : message;

    return (
      <div className={`maintainer-log-message-body ${isLongMessage ? "maintainer-log-message-expandable" : ""} ${isLongMessage && !isExpanded ? "maintainer-log-message-collapsed" : ""}`}>
        {isLongMessage ? (
          <button type="button" className="maintainer-log-message-toggle" aria-label={isExpanded ? "Collapse log message" : "Expand log message"} title={isExpanded ? "Collapse log message" : "Expand log message"} onClick={() => toggleLogMessage(entry.id)}>
            {isExpanded ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
          </button>
        ) : null}
        <pre>{preview}</pre>
      </div>
    );
  }

  function renderPagination(position) {
    return (
      <div className={`maintainer-logs-pagination maintainer-logs-pagination-${position}`}>
        <span>{total ? `Showing ${visibleStart}-${visibleEnd} out of ${total} records` : "Showing 0 out of 0 records"}</span>
        <label className="maintainer-logs-rows">
          <span>Rows</span>
          <select value={filters.pageSize} onChange={(event) => updateFilter("pageSize", Number(event.target.value))}>
            <option value={10}>10</option>
            <option value={25}>25</option>
            <option value={50}>50</option>
            <option value={100}>100</option>
          </select>
        </label>
        <div className="maintainer-logs-page-controls">
          <button type="button" aria-label="First page" onClick={() => goToPage(1)} disabled={filters.page <= 1 || isLoading}>
            <ChevronsLeft size={13} />
          </button>
          <button type="button" aria-label="Previous page" onClick={() => goToPage(filters.page - 1)} disabled={filters.page <= 1 || isLoading}>
            <ChevronLeft size={13} />
          </button>
          <span className="maintainer-logs-page-label">
            Page {filters.page} of {totalPages}
          </span>
          <button type="button" aria-label="Next page" onClick={() => goToPage(filters.page + 1)} disabled={filters.page >= totalPages || isLoading}>
            <ChevronRight size={13} />
          </button>
          <button type="button" aria-label="Last page" onClick={() => goToPage(totalPages)} disabled={filters.page >= totalPages || isLoading}>
            <ChevronsRight size={13} />
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="maintainer-logs-shell" role="presentation" onClick={onClose}>
      <section className="maintainer-logs-view" role="dialog" aria-modal="true" aria-labelledby="maintainer-logs-title" onClick={(event) => event.stopPropagation()}>
        <header>
          <div>
            <span>Maintainer mode</span>
            <h2 id="maintainer-logs-title">Application logs</h2>
          </div>
          <IconButton label="Close logs" onClick={onClose}>
            <X size={18} />
          </IconButton>
        </header>

        <div className="maintainer-logs-toolbar">
          <label className="search-field maintainer-log-search">
            <Search size={14} />
            <input type="search" value={filters.search} onChange={(event) => updateFilter("search", event.target.value)} placeholder="Search logs" />
          </label>
          <label>
            <span>Status</span>
            <select value={filters.status} onChange={(event) => updateFilter("status", event.target.value)}>
              <option value="ALL">All statuses</option>
              {statuses.map((status) => (
                <option key={status} value={status}>
                  {status}
                </option>
              ))}
            </select>
          </label>
          <label>
            <span>From</span>
            <input type="date" value={filters.dateFrom} onChange={(event) => updateFilter("dateFrom", event.target.value)} />
          </label>
          <label>
            <span>To</span>
            <input type="date" value={filters.dateTo} onChange={(event) => updateFilter("dateTo", event.target.value)} />
          </label>
          <button className="tool-button maintainer-refresh-button" type="button" onClick={() => setReloadToken((current) => current + 1)} disabled={isLoading}>
            <RefreshCw size={14} />
            <span>Refresh</span>
          </button>
          <button className="tool-button maintainer-clear-button" type="button" onClick={() => setIsClearConfirmOpen(true)} disabled={!selectedLogIds.size || isLoading || isClearing}>
            <Trash2 size={14} />
            <span>Clear log</span>
          </button>
        </div>

        <StatusBar message={feedback.message} tone={feedback.tone} variant="file" className="maintainer-logs-status" />

        {showTopPagination ? renderPagination("top") : null}

        <div className="maintainer-logs-table-wrap">
          <table className="maintainer-logs-table">
            <thead>
              <tr>
                <th className="maintainer-log-select-cell">
                  <input type="checkbox" aria-label="Select visible log entries" checked={areAllVisibleLogsSelected} onChange={(event) => toggleVisibleLogs(event.target.checked)} disabled={!entries.length || isLoading} />
                </th>
                <th>
                  <button
                    type="button"
                    className={`maintainer-sort-button ${filters.sortBy === "date" ? "is-active" : ""}`}
                    aria-label={`Sort logs by date${filters.sortBy === "date" ? `, currently ${filters.sortDir === "asc" ? "oldest first" : "newest first"}` : ""}`}
                    title="Sort by date"
                    onClick={() => sortBy("date")}
                  >
                    <span>Date</span>
                    {renderDateSortIcon()}
                  </button>
                </th>
                <th>
                  <button type="button" onClick={() => sortBy("status")}>
                    Status{sortLabel("status")}
                  </button>
                </th>
                <th>
                  <button type="button" onClick={() => sortBy("message")}>
                    Message{sortLabel("message")}
                  </button>
                </th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr>
                  <td colSpan="4">
                    <div className="sidebar-loading-dots" role="status" aria-label="Loading logs">
                      <span />
                      <span />
                      <span />
                    </div>
                  </td>
                </tr>
              ) : null}
              {!isLoading && entries.length === 0 ? (
                <tr>
                  <td colSpan="4" className="maintainer-logs-empty">
                    No log entries found.
                  </td>
                </tr>
              ) : null}
              {!isLoading
                ? entries.map((entry, index) => (
                    <tr key={`${entry.date}-${entry.status}-${index}`}>
                      <td className="maintainer-log-select-cell">
                        <input type="checkbox" aria-label={`Select log entry from ${entry.date}`} checked={selectedLogIds.has(String(entry.id))} onChange={(event) => toggleLogSelection(entry.id, event.target.checked)} />
                      </td>
                      <td>
                        <time>{entry.date}</time>
                      </td>
                      <td>
                        <span className={`status-pill status-${statusClass(entry.status)}`}>{entry.status}</span>
                      </td>
                      <td className="maintainer-log-message">{renderLogMessage(entry)}</td>
                    </tr>
                  ))
                : null}
            </tbody>
          </table>
        </div>

        {renderPagination("bottom")}
        <ConfirmDialog
          isOpen={isClearConfirmOpen}
          title="Clear selected logs?"
          dialogId="clear-maintainer-logs-confirm"
          icon={<AlertTriangle size={18} />}
          onClose={() => setIsClearConfirmOpen(false)}
          actions={[
            { label: "Cancel", onClick: () => setIsClearConfirmOpen(false), autoFocus: true },
            { label: isClearing ? "Clearing" : "Clear log", onClick: clearSelectedLogs, variant: "danger", icon: <Trash2 size={15} /> },
          ]}
        >
          <p>
            This will permanently remove {selectedLogIds.size} selected log {selectedLogIds.size === 1 ? "entry" : "entries"} from <strong>logs/app.log</strong>.
          </p>
        </ConfirmDialog>
      </section>
    </div>
  );
}
