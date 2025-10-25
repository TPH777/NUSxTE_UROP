import type { ChangeEvent } from "react";
import { useEffect, useRef, useState } from "react";
import "./FileInput.css";

const STATUS_IDLE = 0;
const STATUS_READY = 1;

type FileInputProps = {
    accept?: string;
    multiple?: boolean;
    onFilesChange?: (files: File[]) => void;
    initialFiles?: File[];
};

export function FileInput({ accept = "*", multiple = true, onFilesChange, initialFiles = [] }: FileInputProps) {
    const [files, setFiles] = useState<File[]>(initialFiles);
    const [status, setStatus] = useState(STATUS_IDLE);
    const inputRef = useRef<HTMLInputElement | null>(null);

    useEffect(() => {
        setFiles(initialFiles);
    }, [initialFiles]);

    const handleFileSelection = (event: ChangeEvent<HTMLInputElement>) => {
        const selected = event.target.files;
        if (!selected || selected.length === 0) {
            return;
        }

        const selectedFiles = Array.from(selected);
        setFiles((prev) => {
            const merged = mergeFiles(prev, selectedFiles);
            setStatus(merged.length > 0 ? STATUS_READY : STATUS_IDLE);
            onFilesChange?.(merged);
            return merged;
        });

        // reset input so same file can be re-selected later
        event.target.value = "";
    };

    const handleRemoveFile = (index: number) => {
        setFiles((prev) => {
            const next = prev.filter((_, i) => i !== index);
            setStatus(next.length > 0 ? STATUS_READY : STATUS_IDLE);
            onFilesChange?.(next);
            return next;
        });
    };

    const handleClearAll = () => {
        setFiles([]);
        setStatus(STATUS_IDLE);
        onFilesChange?.([]);
    };

    const handleBrowse = () => inputRef.current?.click();

    return (
        <div className="file-input">
            <input
                ref={inputRef}
                className="file-input__native"
                type="file"
                accept={accept}
                multiple={multiple}
                onChange={handleFileSelection}
            />

            <div className="file-input__controls">
                <button type="button" className="file-input__button" onClick={handleBrowse}>
                    Select files
                </button>
                <button
                    type="button"
                    className="file-input__button file-input__button--secondary"
                    onClick={handleClearAll}
                    disabled={files.length === 0}
                >
                    Clear
                </button>
            </div>

            <div className="file-input__list" aria-live="polite">
                {files.map((file, index) => {
                    const resolvedPath = getFilePath(file);
                    return (
                    <li key={resolvedPath ?? `${file.name}-${file.size}-${index}`} 
                    className="file-input__list-item"
                    onClick={() => handleRemoveFile(index)}
                    role="button"
                    tabIndex={0}
                    onKeyDown={(event) => {
                        if (event.key === "Enter" || event.key === " ") {
                            handleRemoveFile(index);
                        }
                    }}
                    >
                        <div className="file-input__list-details">
                            <span className="file-input__filename">{file.name}</span>
                            {resolvedPath && <span className="file-input__meta file-input__meta--path">{resolvedPath}</span>}
                        </div>
                    </li>
                );
                })}
                {files.length === 0 && <li className="file-input__placeholder">No files selected yet</li>}
            </div>
        </div>
    );
}

function mergeFiles(existing: File[], incoming: File[]) {
    const seen = new Set(existing.map((file) => fileKey(file)));
    const merged = existing.slice();

    incoming.forEach((file) => {
        const key = fileKey(file);
        if (!seen.has(key)) {
            merged.push(file);
            seen.add(key);
        }
    });

    return merged;
}

function fileKey(file: File) {
    return `${file.name}-${file.size}-${"lastModified" in file ? file.lastModified : 0}-${getFilePath(file) ?? ""}`;
}

function getFilePath(file: File) {
    return (file as File & { path?: string }).path;
}

function formatFileSize(bytes: number) {
    if (bytes === 0) {
        return "0 B";
    }
    const units = ["B", "KB", "MB", "GB", "TB"];
    const exponent = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);
    const size = bytes / Math.pow(1024, exponent);
    return `${size.toFixed(size >= 10 || exponent === 0 ? 0 : 1)} ${units[exponent]}`;
}

