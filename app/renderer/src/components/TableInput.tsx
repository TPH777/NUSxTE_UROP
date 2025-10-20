import "./TableInput.css";
import type { ChangeEvent } from "react";
import { useMemo, useState, useEffect } from "react";
import { FileInput } from "./FileInput";

type TableRow = {
    id: number;
    className: string;
    files: File[];
};

type TableInputProps = {
    initialRows?: number;
};

type FsLike = {
    mkdir: (path: string, options: { recursive: boolean }) => Promise<void>;
    copyFile: (source: string, destination: string) => Promise<void>;
    writeFile: (destination: string, data: Uint8Array) => Promise<void>;
    rm: (path: string, options: {recursive: boolean; force: boolean}) => Promise<void>;
    readdir: (
        path: string,
        options?: {withFileTypes?: boolean}
    ) => Promise<Array<{ name: string; isDirectory(): boolean}>>;
};

type PathLike = {
    join: (...segments: string[]) => string;
};

function TableInput({ initialRows = 1 }: TableInputProps) {
    const [rows, setRows] = useState<TableRow[]>(() => (
        Array.from({ length: initialRows }, (_, index) => ({ className: "", id: index, files: [] }))
    ));
    const [isSaving, setIsSaving] = useState(false);
    const [statusMessage, setStatusMessage] = useState<string | null>(null);
    const [errorMessage, setErrorMessage] = useState<string | null>(null);

    const totalFiles = useMemo(() => rows.reduce((sum, row) => sum + row.files.length, 0), [rows]);

    const updateRowFiles = (rowId: number, files: File[]) => {
        setRows((prev) =>
            prev.map((row) => (row.id === rowId ? { ...row, files } : row)),
        );
    };

    const updateRowClassName = (rowId: number, className: string) => {
        setRows((prev) =>
            prev.map((row) => (row.id === rowId ? { ...row, className } : row)),
        );
    };

    const handleClassNameChange = (rowId: number, event: ChangeEvent<HTMLTextAreaElement>) => {
        autoResize(event.target);
        updateRowClassName(rowId, event.target.value);
    };

    const removeRow = (rowId: number) => {
        setRows((prev) => prev.filter((row) => row.id !== rowId));
    };

    const addRow = () => {
        setRows((prev) => {
            const nextId = prev.length ? Math.max(...prev.map((row) => row.id)) + 1 : 0;
            return [...prev, { id: nextId, className: "", files: [] }];
        });
    };

    const handleSubmit = async () => {
        if (!fs || !nodePath) {
            setErrorMessage("File system APIs are unavailable in this environment.");
            return;
        }

        const rowsWithFiles = rows.filter((row) => row.className.trim() && row.files.length > 0);
        if (rowsWithFiles.length === 0) {
            setErrorMessage("Nothing to save. Add a class name and at least one file before submitting.");
            return;
        }

        setIsSaving(true);
        setErrorMessage(null);
        setStatusMessage(null);

        try {
            let savedFiles = 0;
            const baseDir = window.process?.cwd?.() ?? ".";

            for (const row of rowsWithFiles) {
                const safeClassName = sanitizePathSegment(row.className.trim());
                const classDir = nodePath.join(baseDir, "images", safeClassName);

                await fs.rm(classDir, {recursive: true, force: true});
                await fs.mkdir(classDir, { recursive: true });

                for (const file of row.files) {
                    const sourcePath = getFilePath(file);
                    const destinationPath = nodePath.join(classDir, file.name);

                    if (sourcePath) {
                        if (sourcePath !== destinationPath) {
                            await fs.copyFile(sourcePath, destinationPath);
                        }
                    } else {
                        const fileBuffer = new Uint8Array(await file.arrayBuffer());
                        await fs.writeFile(destinationPath, fileBuffer);
                    }
                    savedFiles += 1;
                }
            }

            setStatusMessage(`Saved ${savedFiles} file${savedFiles === 1 ? "" : "s"} to the images directory.`);
        } catch (error) {
            console.error("Failed to save files", error);
            setErrorMessage(error instanceof Error ? error.message : "Failed to save files.");
        } finally {
            setIsSaving(false);
        }
    };

    useEffect(() => {
        if (!fs || !nodePath) {
            setErrorMessage("File system APIs are unavailable")
            return;
        }

        const loadExisitingRows = async () => {
            try {
                const baseDir = window.process?.cwd?.() ?? ".";
                const imagesDir = nodePath.join(baseDir, "images")
            } catch (error) {
                console.error("Faled to load images", error);
                setErrorMessage(error instanceof Error ? error.message : "Failed to load images")
            }
        }
    }, []);
        
    

    return (
        <div className="table-input">
            <div className="table-input__table-wrapper">
                <table className="table-input__table">
                    <thead>
                        <tr>
                            <th>Class Name</th>
                            <th>Images</th>
                            <th>Image Count</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows.map((row) => (
                            <tr key={row.id}>
                                <td>
                                    <textarea
                                        ref={autoResize}
                                        rows={1}
                                        className="table-input__text"
                                        value={row.className}
                                        placeholder="Enter class"
                                        onChange={(event) => handleClassNameChange(row.id, event)}
                                    />
                                </td>
                                <td className="table-input__file-cell">
                                    <FileInput onFilesChange={(files) => updateRowFiles(row.id, files)} />
                                </td>
                                <td className="table-input__count">
                                    <span className="table-input__count-number">{row.files.length}</span>
                                    <button
                                        type="button"
                                        className="table-input__remove-row"
                                        onClick={() => removeRow(row.id)}
                                    >
                                        Remove
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                    <tfoot>
                        <tr>
                            <td colSpan={2}>Total</td>
                            <td className="table-input__count">
                                <span className="table-input__count-number">{totalFiles}</span>
                            </td>
                        </tr>
                    </tfoot>
                </table>
            </div>

            <div className="table-input__actions">
                <button type="button" className="table-input__add-row" onClick={addRow}>
                    Add row
                </button>
                <button
                    type="button"
                    className="table-input__submit"
                    onClick={handleSubmit}
                    disabled={isSaving}
                >
                    Submit
                </button>
            </div>

            {statusMessage && <p className="table-input__status">{statusMessage}</p>}
            {errorMessage && <p className="table-input__status table-input__status--error">{errorMessage}</p>}
        </div>
    );
}

export default TableInput;

function autoResize(element: HTMLTextAreaElement | null) {
    if (!element) {
        return;
    }
    element.style.height = "auto";
    element.style.height = `${element.scrollHeight}px`;
}

function getFilePath(file: File) {
    return (file as File & { path?: string }).path;
}

function sanitizePathSegment(value: string) {
    return value.replace(/[<>:"/\\|?*]+/g, "_").trim() || "untitled";
}

declare global {
    interface Window {
        require?: (module: string) => unknown;
        process?: {
            cwd?: () => string;
        };
    }
}

const fsModule = typeof window !== "undefined" && typeof window.require === "function"
    ? (window.require("fs") as { promises?: FsLike })
    : undefined;

const fs = fsModule?.promises ?? null;

const nodePath = typeof window !== "undefined" && typeof window.require === "function"
    ? (window.require("path") as PathLike)
    : null;