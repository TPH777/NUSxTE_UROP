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
    imageNames: string[]; // Change from images to imageNames
};

function Generate() {
    console.log('=== GENERATE COMPONENT MOUNTED ===');
    
    const [generateConfigs, setGenerateConfigs] = useState<GenerateConfig[]>([]);
    const [classProgress, setClassProgress] = useState<ClassProgress[]>([]);
    const [totalExpected, setTotalExpected] = useState<number>(0);
    const [totalGenerated, setTotalGenerated] = useState<number>(0);
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    const [hoveredImage, setHoveredImage] = useState<string | null>(null);
    const [hoveredImagePath, setHoveredImagePath] = useState<string | null>(null); // Add this
    const [expandedClasses, setExpandedClasses] = useState<Set<number>>(new Set());

    console.log('Generate component state:', { isLoading, error, configsLength: generateConfigs.length });

    // Load generate configs on mount
    useEffect(() => {
        console.log('=== LOAD GENERATE CONFIGS useEffect RUNNING ===');
        
        const loadGenerateConfigs = async () => {
            console.log('loadGenerateConfigs function called');
            try {
                console.log('window.require exists?', !!window.require);
                
                if (!window.require) {
                    console.error('window.require is undefined!');
                    setError('Electron APIs not available');
                    setIsLoading(false);
                    return;
                }

                const electron = window.require('electron') as any;
                const { ipcRenderer } = electron;
                
                console.log('Invoking read-generate-queue...');
                const result = await ipcRenderer.invoke('read-generate-queue');
                
                console.log('Generate queue result:', result);

                if (result && result.success && result.generateConfigs) {
                    console.log('Generate configs loaded:', result.generateConfigs);
                    setGenerateConfigs(result.generateConfigs);
                    
                    const total = result.generateConfigs.reduce(
                        (sum: number, config: GenerateConfig) => sum + config.num_samples, 
                        0
                    );
                    setTotalExpected(total);
                    setError(null);
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
        console.log('=== POLLING useEffect ===');
        console.log('generateConfigs:', generateConfigs);
        
        if (generateConfigs.length === 0) {
            console.log('No configs yet, skipping polling');
            return;
        }

        const countGeneratedImages = async () => {
            console.log('=== countGeneratedImages called ===');
            try {
                if (!window.require) {
                    console.log('window.require not available');
                    return;
                }

                const electron = window.require('electron') as any;
                const { ipcRenderer } = electron;

                const progressPromises = generateConfigs.map(async (config, index) => {
                    console.log(`Counting images for config ${index}:`, config);
                    
                    const result = await ipcRenderer.invoke(
                        'count-generated-images',
                        config.name,
                        config.prompt
                    );

                    console.log(`Result for ${config.prompt}:`, result);

                    return {
                        prompt: config.prompt,
                        expected: config.num_samples,
                        generated: result.success ? result.count : 0,
                        isComplete: result.success && result.count >= config.num_samples,
                        imageNames: result.success ? result.imageNames : [], // Change to imageNames
                    };
                });

                const progress = await Promise.all(progressPromises);
                console.log('All progress results:', progress);
                
                setClassProgress(progress);

                const total = progress.reduce((sum, p) => sum + p.generated, 0);
                console.log('Total generated images:', total);
                setTotalGenerated(total);
            } catch (err) {
                console.error('Error counting generated images:', err);
            }
        };

        console.log('Running initial count...');
        countGeneratedImages();

        console.log('Setting up polling interval (3000ms)');
        const intervalId = setInterval(countGeneratedImages, 3000);

        return () => {
            console.log('Cleaning up polling interval');
            clearInterval(intervalId);
        };
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

    // Update the handleImageHover function (around line 174)
    const handleImageHover = async (classIndex: number, imageName: string) => {
        if (!window.require) return;
        
        console.log('Hovering over image:', imageName);
        
        try {
            const electron = window.require('electron') as any;
            const { ipcRenderer } = electron;
            
            const config = generateConfigs[classIndex];
            console.log('Loading image with config:', config.name, config.prompt, imageName);
            
            const result = await ipcRenderer.invoke(
                'get-image-data',
                config.name,
                config.prompt,
                imageName
            );
            
            console.log('Image load result:', result.success ? 'success' : result.error);
            
            if (result.success) {
                setHoveredImage(imageName);
                setHoveredImagePath(result.dataUrl); // Use dataUrl instead of path
            }
        } catch (err) {
            console.error('Error loading image:', err);
        }
    };

    const handleImageLeave = () => {
        setHoveredImage(null);
        setHoveredImagePath(null);
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

                            {/* Image List (names only) */}
                            {isExpanded && progress.imageNames.length > 0 && (
                                <div className="generate__image-list">
                                    {progress.imageNames.map((imageName, imgIndex) => (
                                        <div 
                                            key={imgIndex}
                                            className="generate__image-item"
                                            onMouseEnter={() => handleImageHover(index, imageName)}
                                            onMouseLeave={handleImageLeave}
                                        >
                                            <span className="generate__image-icon">🖼️</span>
                                            <span className="generate__image-name">{imageName}</span>
                                        </div>
                                    ))}
                                </div>
                            )}

                            {isExpanded && progress.imageNames.length === 0 && (
                                <div className="generate__no-images">
                                    No images generated yet
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>

            {/* Hover Preview */}
            {hoveredImage && hoveredImagePath && (
                <div className="generate__hover-preview">
                    <div className="generate__hover-preview-header">
                        {hoveredImage}
                    </div>
                    <img 
                        src={hoveredImagePath}  // Remove file://, now it's a data URL
                        alt={hoveredImage}
                        onError={(e) => {
                            console.error('Image failed to load:', hoveredImage);
                            console.error('Data URL length:', hoveredImagePath?.length);
                        }}
                    />
                </div>
            )}
        </div>
    );
}

export default Generate;