import "./AdvanceConfigPanel.css";
import {useState, useEffect} from "react";
import configSchema from "../utils/default-config-schema.json";

type ConfigValues = Record<string, number>;

type FieldSchema = {
    key: string;
    label: string;
    type: string;
    min?: number;
    max?: number;
    step?: number;
    default: number;
};

type SectionSchema = {
    label: string;
    fields: FieldSchema[];
};

type ConfigPanelProps = {
    onConfigChange?: (config: ConfigValues) => void;
};

export function AdvanceConfigPanel({onConfigChange}: ConfigPanelProps) {
    const [config, setConfig] = useState<ConfigValues>({})

    // load config on mount
    useEffect(() => {
        loadConfig();
    }, []);

    const loadConfig = async() => {
        if (!fs || !nodePath) return;

        try {
            const baseDir = window.process?.cwd?.() ?? ".";
            const configPath = nodePath.join(baseDir, "advance-config-values.json")

            const data = await fs.readFile(configPath, 'utf-8');
            const loadedConfig = JSON.parse(data);
            setConfig(loadedConfig);
            onConfigChange?.(loadedConfig);
        } catch (error) {
            console.log("No config file found, using defaults");
            //default
            const defaults: ConfigValues = {};
            Object.values(configSchema).forEach((section: any) => {
                section.fields.forEach((field: FieldSchema) => {
                    defaults[field.key] = field.default
                });
            });
            setConfig(defaults);
            onConfigChange?.(defaults);
        }
    };

    const saveConfig = async () => {
        if (!fs || !nodePath) return;

        try {
            const baseDir = window.process?.cwd?.() ?? ".";
            const configPath = nodePath.join(baseDir, "advance-config-values.json");

            await fs.writeFile(configPath, JSON.stringify(config, null, 2));
            console.log("Config saved successfully");
        } catch (error) {
            console.error("Failed to save config:", error);
        }
    };

    const handleChange = (key: string, value: number) => {
        const newConfig = {...config, [key]: value};
        setConfig(newConfig);
        onConfigChange?.(newConfig);
    }

    return (
        <div className="advance-config-panel">
            <div className="advance-config-panel__header">
                <button 
                    type="button"
                    className="advance-config-panel__save-btn"
                    onClick = {saveConfig}
                >
                    Save Config
                </button>
            </div>

            {Object.entries(configSchema).map(([sectionKey, section]) => {
                const typedSection = section as SectionSchema;
                return (
                    <div key = {sectionKey} className="advance-config-panel__section">
                        <h4>{typedSection.label}</h4>
                        <div className="advance-config-panel__row">
                            {typedSection.fields.map((field) => {
                                return (
                                    <label key={field.key}>
                                        {field.label}:
                                        <input
                                            type={field.type}
                                            min={field.min}
                                            max={field.max}
                                            step={field.step}
                                            value={config[field.key] ?? field.default}
                                            onChange={(e) => handleChange(field.key, parseFloat(e.target.value))}
                                            />
                                    </label>
                                );
                            })}
                        </div>
                    </div>
                )
            })}


        </div>
    )
}

// file system declarations
type FsLike = {
    readFile: (path: string, encoding: string) => Promise<string>;
    writeFile: (path: string, data: string) => Promise<void>;
};

type PathLike = {
    join: (...segments: string[]) => string;
};

declare global {
    interface Window {
        require?: (module: string) => unknown;
        process?: {
            cwd?: () => string;
        };
    }
}

const fsModule = typeof window !== "undefined" && typeof window.require === "function"
    ? (window.require("fs") as { promises?: FsLike})
    : undefined;

const fs = fsModule?.promises ?? null;

const nodePath = typeof window !== "undefined" && typeof window.require === "function"
    ? (window.require("path") as PathLike)
    : null;