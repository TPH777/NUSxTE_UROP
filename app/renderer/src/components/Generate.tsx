import { useState, useEffect } from 'react';
import './Generate.css';

declare global {
    interface Window {
        require: ((module: string) => any) | undefined;
    }
}

type GenerateConfig = {
    name: string;
    prompt: string;
    num_samples: number;
    resolution: number;
    num_inference_steps: number;
    guidance_scale: number;
};

type ClassProgress = {
    prompt: string;
    expected: number;
    generated: number;
    isComplete: boolean;
    images: string[]; // Add this
};

function Generate() {
    const [generateConfigs, setGenerateConfigs] = useState<GenerateConfig[]>([]);
    const [classProgress, setClassProgress] = useState<ClassProgress[]>([]);
    const [totalExpected, setTotalExpected] = useState<number>(0);
    const [totalGenerated, setTotalGenerated] = useState<number>(0);
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    const [hoveredImage, setHoveredImage] = useState<string | null>(null);
    const [expandedClasses, setExpandedClasses] = useState<Set<number>>(new Set());

    // Load generate configs on mount
    useEffect(() => {
        const loadGenerateConfigs = async () => {
            try {
                if (!window.require) {
                    setError('Electron APIs not available');
                    setIsLoading(false);
                    return;
                }

                const electron = window.require('electron') as any;
                const { ipcRenderer } = electron;
                const result = await ipcRenderer.invoke('read-generate-queue');

                console.log('Generate queue result:', result); // Debug log

                if (result && result.success && result.generateConfigs) {
                    console.log('Generate configs loaded:', result.generateConfigs);
                    setGenerateConfigs(result.generateConfigs);
                    
                    // Calculate total expected
                    const total = result.generateConfigs.reduce(
                        (sum: number, config: GenerateConfig) => sum + config.num_samples, 
                        0
                    );
                    setTotalExpected(total);
                    setError(null); // Clear any previous errors
                } else {
                    const errorMsg = result?.error || 'Failed to load generate queue - no data returned';
                    console.error('Failed to load generate queue:', errorMsg);
                    setError(errorMsg);
                }
            } catch (err) {
                console.error('Error loading generate configs:', err);
                setError(err instanceof Error ? err.message : 'Failed to load generate configurations');
            } finally {
                setIsLoading(false);
            }
        };

        loadGenerateConfigs();
    }, []);

    // Poll for generated images
    useEffect(() => {
        if (generateConfigs.length === 0) return;

        const countGeneratedImages = async () => {
            try {
                if (!window.require) return;

                const electron = window.require('electron') as any;
                const { ipcRenderer } = electron;

                const progressPromises = generateConfigs.map(async (config) => {
                    const result = await ipcRenderer.invoke(
                        'count-generated-images',
                        config.name,
                        config.prompt
                    );

                    return {
                        prompt: config.prompt,
                        expected: config.num_samples,
                        generated: result.success ? result.count : 0,
                        isComplete: result.success && result.count >= config.num_samples,
                        images: result.success ? result.images : [],
                    };
                });

                const progress = await Promise.all(progressPromises);
                setClassProgress(progress);

                // Calculate total generated
                const total = progress.reduce((sum, p) => sum + p.generated, 0);
                setTotalGenerated(total);
            } catch (err) {
                console.error('Error counting generated images:', err);
            }
        };

        // Initial count
        countGeneratedImages();

        // Poll every 3 seconds
        const intervalId = setInterval(countGeneratedImages, 3000);

        return () => clearInterval(intervalId);
    }, [generateConfigs]);

    const toggleClassExpanded = (index: number) => {
        setExpandedClasses(prev => {
            const newSet = new Set(prev);
            if (newSet.has(index)) {
                newSet.delete(index);
            } else {
                newSet.add(index);
            }
            return newSet;
        });
    };

    if (isLoading) {
        return (
            <div className="generate">
                <h2>Image Generation</h2>
                <div className="generate__loading">Loading generation queue...</div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="generate">
                <h2>Image Generation</h2>
                <div className="generate__error">{error}</div>
            </div>
        );
    }

    const overallProgress = totalExpected > 0 
        ? Math.round((totalGenerated / totalExpected) * 100) 
        : 0;

    const allComplete = classProgress.length > 0 && 
        classProgress.every(p => p.isComplete);

    return (
        <div className="generate">
            <h2>Image Generation</h2>

            {/* Overall Progress */}
            <div className="generate__overall">
                <div className="generate__overall-header">
                    <span>Total Progress</span>
                    <span>{totalGenerated} / {totalExpected} images</span>
                </div>
                <div className="generate__progress-bar">
                    <div 
                        className="generate__progress-fill"
                        style={{ width: `${overallProgress}%` }}
                    />
                </div>
                <div className="generate__overall-footer">
                    {overallProgress}% Complete
                </div>
            </div>

            {/* Completion Status */}
            {allComplete && (
                <div className="generate__complete">
                    ✓ All images generated successfully!
                </div>
            )}

            {/* Per-Class Progress */}
            <div className="generate__classes">
                <h3>Generation Progress by Class</h3>
                {classProgress.map((progress, index) => {
                    const classProgress = progress.expected > 0
                        ? Math.round((progress.generated / progress.expected) * 100)
                        : 0;
                    
                    const isExpanded = expandedClasses.has(index);

                    return (
                        <div key={index} className="generate__class-item">
                            <div 
                                className="generate__class-header"
                                onClick={() => toggleClassExpanded(index)}
                                style={{ cursor: 'pointer' }}
                            >
                                <span className="generate__class-name">
                                    <span className="generate__expand-icon">
                                        {isExpanded ? '▼' : '▶'}
                                    </span>
                                    {progress.prompt}
                                </span>
                                <span className="generate__class-count">
                                    {progress.generated} / {progress.expected}
                                    {progress.isComplete && (
                                        <span className="generate__class-badge">✓</span>
                                    )}
                                </span>
                            </div>
                            <div className="generate__progress-bar generate__progress-bar--small">
                                <div 
                                    className="generate__progress-fill"
                                    style={{ width: `${classProgress}%` }}
                                />
                            </div>

                            {/* Image Gallery */}
                            {isExpanded && progress.images.length > 0 && (
                                <div className="generate__image-gallery">
                                    {progress.images.map((imagePath, imgIndex) => (
                                        <div 
                                            key={imgIndex}
                                            className="generate__image-container"
                                            onMouseEnter={() => setHoveredImage(imagePath)}
                                            onMouseLeave={() => setHoveredImage(null)}
                                        >
                                            <img 
                                                src={`file://${imagePath}`}
                                                alt={`Generated ${progress.prompt} ${imgIndex + 1}`}
                                                className="generate__image-thumbnail"
                                            />
                                        </div>
                                    ))}
                                </div>
                            )}

                            {isExpanded && progress.images.length === 0 && (
                                <div className="generate__no-images">
                                    No images generated yet
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>

            {/* Hover Preview */}
            {hoveredImage && (
                <div className="generate__hover-preview">
                    <img 
                        src={`file://${hoveredImage}`}
                        alt="Preview"
                    />
                </div>
            )}
        </div>
    );
}

export default Generate;