import "./TableInput.css";
import type { ChangeEvent } from "react";
import { useMemo, useState, useEffect, useContext } from "react";
import { FileInput } from "./FileInput";
import { AdvanceConfigPanel } from "./AdvanceConfigPanel";
import configSchema from "../utils/default-config-schema.json";
import { StageContext } from "../context/StageContext";
import { QueueContext } from "../context/QueueContext";

type TableRow = {
    id: number;
    className: string;
    files: File[];
    config?: Record<string, number | boolean>;
};

type TableInputProps = {
    initialRows?: number;
};

type FsLike = {
    mkdir: (path: string, options: { recursive: boolean }) => Promise<void>;
    copyFile: (source: string, destination: string) => Promise<void>;
    writeFile: (destination: string, data: Uint8Array) => Promise<void>;
    rm: (path: string, options: {recursive: boolean; force: boolean}) => Promise<void>;
    readdir: {
        (path: string): Promise<string[]>
        (path: string,
            options?: {withFileTypes?: boolean}):  Promise<Array<{ name: string; isDirectory(): boolean}>>;
    }
};

type PathLike = {
    join: (...segments: string[]) => string;
};

type FileSource = 'disk' | 'user' | 'unknown';

function getFileSource(file: File): FileSource {
    const path = getFilePath(file);
    if (path) return 'disk';
    if (typeof file.arrayBuffer === 'function') return 'user';
    return 'unknown';
}

function getConfigDefault(key: string): number {
    for (const section of Object.values(configSchema)) {
        const field = (section as any).fields.find((f: any) => f.key === key);
        if (field) return field.default;
    }
    return 0;
}
function TableInput({ initialRows = 1 }: TableInputProps) {
    const stageContext = useContext(StageContext);
    const queueContext = useContext(QueueContext);

    const [rows, setRows] = useState<TableRow[]>(() => (
        Array.from({ length: initialRows }, (_, index) => ({ className: "", id: index, files: [] }))
    ));
    const [isSaving, setIsSaving] = useState(false);
    const [statusMessage, setStatusMessage] = useState<string | null>(null);
    const [errorMessage, setErrorMessage] = useState<string | null>(null);


    // set configs
    const [config, setConfig] = useState<Record<string, number | boolean>>(() => {
        const defaults: Record<string, number | boolean> = {};
        for (const section of Object.values(configSchema)) {
            (section as any).fields.forEach((field: any) => {
                defaults[field.key] = field.default;
            });
        }
        return defaults;
    })

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

    const handleTrain = async () => {
        if (!fs || !nodePath) {
            setErrorMessage("File system APIs are unavailable in this environment.");
            return;
        }

        const rowsWithFiles = rows.filter((row) => row.className.trim() && row.files.length > 0);
        if (rowsWithFiles.length === 0) {
            setErrorMessage("Nothing to train. Add a class name and at least one file before training.");
            return;
        } 

        try {
            const baseDir = window.process?.cwd?.() ?? ".";

            // Generate training queue JSON
            const trainingQueue = rowsWithFiles.map((row) => {
                const className = sanitizePathSegment(row.className.trim());

                const trainingConfig: Record<string, any> = {
                    name: className,
                    prompt: "",
                    dataset_path: nodePath.join(baseDir, "dataset", "train", className),
                };
                
                // for each row, add training param 
                for (const [key, value] of Object.entries(config)) {
                    // only include training params, not split ratios
                    if (!key.includes('Ratio') && !key.includes('split')) {
                        trainingConfig[key] = value;
                    }
                }
                
                return trainingConfig;
            });

            // save to json
            const queuePath = nodePath.join(baseDir, "training-queue.json");
            const jsonString = JSON.stringify(trainingQueue, null, 2);
            const jsonBuffer = new TextEncoder().encode(jsonString);
            await fs.writeFile(queuePath, jsonBuffer);

            console.log("Training queue saved:", trainingQueue);
        
            stageContext?.setCurrentStage(1);
            stageContext?.setFurthestStage(1);
            setStatusMessage(`Training started! ${trainingQueue.length} class(es) queued.`);

        } catch(error) {
            console.error("Failed to create training queue:", error);
            setErrorMessage(error instanceof Error ? error.message : "Failed to start training.")
        }

    }

    const handleSavePhotos = async () => {
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

                await fs.mkdir(classDir, { recursive: true });

                let existingFiles: string[] = [];
                try {
                    existingFiles = await fs.readdir(classDir);
                } catch (error) {
                    existingFiles = [];
                }
                
                //set of files that the user wants to keep
                const desiredFiles = new Set(row.files.map(f => f.name));

                // delete files that not on user list
                for (const existingFile of existingFiles) {
                    if (!desiredFiles.has(existingFile)) {
                        const fileToDelete = nodePath.join(classDir, existingFile);
                        await fs.rm(fileToDelete, {recursive: false, force: true});
                        console.log(`Deleted: ${existingFile}`);
                    }
                }

                // Add or update files from user list

                for (const file of row.files) {
                    const sourcePath = getFilePath(file);
                    const destinationPath = nodePath.join(classDir, file.name);
                    const source = getFileSource(file);

                    //skip if alr saved
                    if ((file as any)._savedToDisk && existingFiles.includes(file.name)) {
                        console.log(`Skipping ${file.name} -- already saved`);
                        savedFiles += 1;
                        continue;
                    }
                    switch (source) {
                        case 'disk':
                            //alr on disk, copy if diff location
                            if (sourcePath && sourcePath !== destinationPath) {
                                await fs.copyFile(sourcePath, destinationPath)
                            }
                            savedFiles += 1;
                            break;
                        
                        case 'user':
                            // file user js selected
                            const fileBuffer = new Uint8Array(await file.arrayBuffer());
                            await fs.writeFile(destinationPath, fileBuffer);
                            savedFiles += 1
                            break;

                        case 'unknown':
                            console.warn(`Skipping unknown file: ${file.name}`);
                            break;
                    }
                }
            }

            // delete class folder that user remove
            const imagesDir = nodePath.join(baseDir, "images");

            try {
                const existingClassDirs = await fs.readdir(imagesDir, {withFileTypes: true});
                const currentClassNames = new Set(
                    rows.map(row => sanitizePathSegment(row.className.trim())).filter(name => name)
                );

                for (const entry of existingClassDirs) {
                    if (entry.isDirectory() && !currentClassNames.has(entry.name)) {
                        const dirToDelete = nodePath.join(imagesDir, entry.name);
                        await fs.rm(dirToDelete, {recursive: true, force: true});
                        console.log(`Deleted class folder: ${entry.name}`);
                    }
                }
            } catch (error) {
                console.warn("Could not clean up removed class folders:", error);
            }
            setStatusMessage(`Saved ${savedFiles} file${savedFiles === 1 ? "" : "s"} to the images/ and created dataset splits directory.`);

            const datasetDir = nodePath.join(baseDir, "dataset");

            // clean out old dataset directory
            try {
                await fs.rm(datasetDir, { recursive: true, force: true});
            } catch (error) {
                //directory not exist
            }

            // new dataset structure
            for (const split of ['train', 'test', 'valid']) {
                for (const row of rowsWithFiles) {
                    const safeClassName = sanitizePathSegment(row.className.trim());
                    const splitDir = nodePath.join(datasetDir, split, safeClassName);
                    await fs.mkdir(splitDir, {recursive: true});
                }
            }

            // copy files to their assigned splits
            for (const row of rowsWithFiles) {
                const safeClassName = sanitizePathSegment(row.className.trim());

                for (const file of row.files) {
                    const split = getFileSplit(
                        file.name,
                        config.splitRandomSeed as number,
                        config.trainRatio as number,
                        config.testRatio as number
                    );
                    console.log(`File: ${file.name} -> Split: ${split} (seed: ${config.splitRandomSeed})`);
                    const sourcePath = nodePath.join(baseDir, "images", safeClassName, file.name);
                    const destPath = nodePath.join(datasetDir, split, safeClassName, file.name);

                    try {
                        await fs.copyFile(sourcePath, destPath);
                        console.log(`Copied ${file.name} to ${split}/${safeClassName}/`);
                    } catch (error) {
                        console.error(`Failed to copy ${file.name} to ${split}:`, error);
                    }
                }
            }
            console.log("Dataset splits created successfully")

        } catch (error) {
            console.error("Failed to save files", error);
            setErrorMessage(error instanceof Error ? error.message : "Failed to save files.");
        } finally {
            setIsSaving(false);
        }
    };

    useEffect(() => {
        if (!fs || !nodePath) return;

        const ensureImagesDir = async () => {
            try {
                const baseDir = window.process?.cwd?.() ?? ".";
                const imagesDir = nodePath.join(baseDir, "images");
                await fs.mkdir(imagesDir, {recursive: true});
                console.log("images directory ensured");
            } catch (error) {
                console.error("Failed to create images directory:", error);
            }
        };

        ensureImagesDir();
    }, []);

    useEffect(() => {
        if (!fs || !nodePath) {
            setErrorMessage("File system APIs are unavailable")
            return;
        }

        const loadExisitingRows = async () => {
            try {
                const baseDir = window.process?.cwd?.() ?? ".";
                const imagesDir = nodePath.join(baseDir, "images")

                const entries = await fs.readdir(imagesDir, {withFileTypes: true});

                const loadedRows = [];
                let nextId = 0;

                for (const entry of entries) {
                    if(!entry.isDirectory()) continue;

                    const className = entry.name;
                    const classDir = nodePath.join(imagesDir, className);
                    const filenames = await fs.readdir(classDir);

                    const filesForRow = [];

                    for (const filename of filenames) {
                        filesForRow.push({
                            name: filename,
                        } as unknown as File);
                    }

                    loadedRows.push({
                        id: nextId++,
                        className,
                        files: filesForRow,
                    });
                }

                setRows(loadedRows.length > 0 ? loadedRows : [
                    { id: 0, className: "", files: [],}
                ]);

            } catch (error) {
                console.error("Faled to load images", error);
                setErrorMessage(error instanceof Error ? error.message : "Failed to load images")
            }
        };

        loadExisitingRows();
    }, []);
        
    


    return (
      <div className="table-input-wrapper">
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
                                    <FileInput 
                                        initialFiles={row.files}
                                        onFilesChange={(files) => updateRowFiles(row.id, files)} />
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
                    onClick={handleSavePhotos}
                    disabled={isSaving}
                >
                    Save Photos
                </button>
                <button
                    type="button"
                    className="table-input__train"
                    onClick={handleTrain}
                    disabled={isSaving}
                >
                    Train
                </button>
            </div>

            {statusMessage && <p className="table-input__status">{statusMessage}</p>}
            {errorMessage && <p className="table-input__status table-input__status--error">{errorMessage}</p>}

            <AdvanceConfigPanel
                onConfigChange={setConfig}
            />
        </div>
      </div>
    );
}

export default TableInput;

function seededRandom(seed: number): () => number {
    let state = seed;
    return () => {
        const BIG_MODULUS = 4294967296;
        const BIG_CONSTANT = 1013904223;
        const BIG_FACTOR = 1664525;
        state = (state * BIG_FACTOR + BIG_CONSTANT) % BIG_MODULUS;
        return state / BIG_MODULUS;
    }
}

function getFileSplit(
    fileName: string,
    seed: number,
    trainRatio: number,
    testRatio: number,
): 'train' | 'test' | 'valid' {
    // create hash from filename + seed
    let hash = seed;
    for (let i = 0; i < fileName.length; i ++) {
        const char = fileName.charCodeAt(i);
        hash = ((hash << 5 ) - hash) + char;
        hash = hash & hash;
    }

    const prng = splitmix32(hash);
    const value = prng();

    console.log(`Created random value ${value}`)
    if (value < trainRatio) return 'train';
    if (value < trainRatio + testRatio) return 'test';
    return 'valid';

}

// pseudo random number generator by MurmurHash3, Mulberry32
function splitmix32(a: number) {
    return function() {
        a |= 0;
        a = a + 0x9e3779b9 | 0;
        let t = a ^ a >>> 16;
        t = Math.imul(t, 0x21f0aaad);
        t = t ^ t >>> 15;
        t = Math.imul(t, 0x735a2d97);
        return ((t = t ^ t >>> 15) >>> 0) / 4294967296;
    }
}

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