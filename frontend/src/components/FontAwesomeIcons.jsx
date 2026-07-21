import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faGithub } from "@fortawesome/free-brands-svg-icons";
import {
  faArrowsRotate,
  faAnglesLeft,
  faAnglesRight,
  faChevronUp,
  faChevronDown,
  faChevronLeft,
  faChevronRight,
  faCodeBranch,
  faCodeMerge,
  faDownload,
  faEraser,
  faEye,
  faEyeSlash,
  faFile,
  faFileCirclePlus,
  faFileCode,
  faFileCsv,
  faFileLines,
  faFilePdf,
  faFileWord,
  faFileZipper,
  faFloppyDisk,
  faKey,
  faMagnifyingGlass,
  faMaximize,
  faPaperclip,
  faPause,
  faPenNib,
  faPlay,
  faPlus,
  faQuestionCircle,
  faRightFromBracket,
  faRightToBracket,
  faSliders,
  faTrashCan,
  faTriangleExclamation,
  faTurnDown,
  faUpload,
  faUser,
  faXmark,
} from "@fortawesome/free-solid-svg-icons";

function makeIcon(icon) {
  return function FontAwesomeShimIcon({ size = 16, style, ...props }) {
    return (
      <FontAwesomeIcon
        aria-hidden="true"
        icon={icon}
        style={{
          width: size,
          height: size,
          fontSize: size,
          ...style,
        }}
        {...props}
      />
    );
  };
}

export const AlertTriangle = makeIcon(faTriangleExclamation);
export const ChevronsLeft = makeIcon(faAnglesLeft);
export const ChevronsRight = makeIcon(faAnglesRight);
export const ChevronDown = makeIcon(faChevronDown);
export const ChevronLeft = makeIcon(faChevronLeft);
export const ChevronRight = makeIcon(faChevronRight);
export const ChevronUp = makeIcon(faChevronUp);
export const CornerDownRight = makeIcon(faTurnDown);
export const Download = makeIcon(faDownload);
export const Eraser = makeIcon(faEraser);
export const Eye = makeIcon(faEye);
export const EyeOff = makeIcon(faEyeSlash);
export const File = makeIcon(faFile);
export const FileCode = makeIcon(faFileCode);
export const FileCsv = makeIcon(faFileCsv);
export const FileLines = makeIcon(faFileLines);
export const FilePdf = makeIcon(faFilePdf);
export const FilePlus2 = makeIcon(faFileCirclePlus);
export const FileWord = makeIcon(faFileWord);
export const FileZipper = makeIcon(faFileZipper);
export const GitBranch = makeIcon(faCodeBranch);
export const GitMerge = makeIcon(faCodeMerge);
export const Github = makeIcon(faGithub);
export const HelpCircle = makeIcon(faQuestionCircle);
export const KeyRound = makeIcon(faKey);
export const LogIn = makeIcon(faRightToBracket);
export const LogOut = makeIcon(faRightFromBracket);
export const Maximize2 = makeIcon(faMaximize);
export const PanelTopClose = makeIcon(faChevronUp);
export const PanelTopOpen = makeIcon(faChevronDown);
export const Paperclip = makeIcon(faPaperclip);
export const Pause = makeIcon(faPause);
export const Pencil = makeIcon(faPenNib);
export const Play = makeIcon(faPlay);
export const Plus = makeIcon(faPlus);
export const RefreshCw = makeIcon(faArrowsRotate);
export const Save = makeIcon(faFloppyDisk);
export const Search = makeIcon(faMagnifyingGlass);
export const SlidersHorizontal = makeIcon(faSliders);
export const Trash2 = makeIcon(faTrashCan);
export const Upload = makeIcon(faUpload);
export const User = makeIcon(faUser);
export const X = makeIcon(faXmark);
