import {useState, useEffect} from 'react';
import './ShowTraining.css'

type TrainingState = {
    progress: number;
    currentStep: number;
    totalSteps: number;
    timeElapsed: string;
    timeRemaining: string;
    currentLoss: number;
    recentLosses: number[];
    avgLoss: number;
    learningRate: number;
    lastCheckpoint: string;
    lastSaved: string;
}

declare global {
    interface Window {
        require: (module: string) => any;
    }
}


function ShowTraining(){
    const [trainingState, setTrainingState] = useState<TrainingState | null>(null);
    const [showDetailedStats, setShowDetailedStats] = useState(false);
    const [lastUpdate, setLastUpdate] = useState<number>(Date.now());
    const [isStale, setIsStale] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const pollInterval = 5000 // 5 seconds
        const staleThreshold = pollInterval * 12 // 1 minute - consider stale if no update

        const readTrainingLog = async () => {
            try {
                // Use IPC to read file from main process
                const { ipcRenderer } = window.require('electron');
                const result = await ipcRenderer.invoke('read-training-log');
                
                console.log('IPC result:', result);
                
                if (!result.success) {
                    setError(`Training log error: ${result.error}`);
                    return;
                }

                const parsed = parseTrainingLog(result.content);
                if (parsed) {
                    setTrainingState(parsed);
                    setLastUpdate(Date.now());
                    setIsStale(false);
                    setError(null);
                }
            } catch (err) {
                console.error('Error reading training log:', err);
                setError('Unable to read training log. Check if training has started.');
            }
        }
        readTrainingLog();

        const intervalId = setInterval(readTrainingLog, pollInterval);

        const staleCheckId = setInterval(() => {
            const timeSinceUpdate = Date.now() - lastUpdate;
            setIsStale(timeSinceUpdate > staleThreshold);
        }, 5000);

        return () => {
            clearInterval(intervalId);
            clearInterval(staleCheckId);
        };
    }, [lastUpdate]);


    const parseTrainingLog = (content: string): TrainingState | null => {
        console.log('Parsing log, content length:', content.length);
        console.log('First 200 chars:', content.substring(0, 200));
        
        const lines = content.trim().split('\n');
        console.log('Total lines:', lines.length);
        const recentLosses: number[] = [];
        let latestState: Partial<TrainingState> = {};
        let lastCheckpoint = '';
        let lastSaved = '';

        //process lines from end
        for (let i = lines.length - 1; i >= 0 && recentLosses.length < 5; i--) {
            const line = lines[i];

            // Parse progress line: "Steps:  83%|████████▎ | 2500/3000 [3:19:27<39:53,  4.79s/it, lr=0.0002, step_loss=0.0263]"
            const progressMatch = line.match(/Steps:\s+(\d+)%.*?\|\s+(\d+)\/(\d+)\s+\[([^\]<]+)(?:<([^\],]+))?,\s+[\d.]+s\/it,\s+lr=([\d.eE+-]+),\s+step_loss=([\d.]+)\]/);

            if (progressMatch) {
                if (recentLosses.length === 0) {
                    latestState = {
                        progress: parseInt(progressMatch[1]),
                        currentStep: parseInt(progressMatch[2]),
                        totalSteps: parseInt(progressMatch[3]),
                        timeElapsed: progressMatch[4],
                        timeRemaining: progressMatch[5],
                        learningRate: parseFloat(progressMatch[6]),
                        currentLoss: parseFloat(progressMatch[7]),
                    };
                }
                recentLosses.push(parseFloat(progressMatch[7]))
            }
            
            //Parse checkpoint save
            const checkpointMatch = line.match(/Model weights saved in [^/]+\/(checkpoint-\d+)/);
            if (checkpointMatch && !lastCheckpoint) {
                lastCheckpoint = checkpointMatch[1];
            }


            //parse saved state
            const savedMatch = line.match(/Saved state to .*\/(checkpoint-\d+)/);
            if (savedMatch && !lastSaved) {
                lastSaved = savedMatch[1];
            }
        }

        if (Object.keys(latestState).length === 0) {
            return null;
        }

        const avgLoss = recentLosses.length > 0
            ? recentLosses.reduce((a, b) => a + b, 0) / recentLosses.length
            : 0;
        
        return {
            ...latestState,
            recentLosses,
            avgLoss,
            lastCheckpoint: lastCheckpoint || 'None',
            lastSaved: lastSaved || 'None',
        } as TrainingState;
    };

    return (
        <div className="show-training">
            <h2> Training Progress</h2>

            {error && (
                <div className="show-training__error"> 
                    {error}
                </div>
            )}

            {isStale && trainingState && (
                <div className="show-training__warning">
                    Training appears to have stopped. Last update: {Math.floor((Date.now() - lastUpdate) / 1000)}s ago
                </div>
            )}

            {!trainingState && !error && (
                <div className="show-training__empty">
                    Waiting for training to start...
                </div>
            )}

            {trainingState && (

                <>
                    <div className="show-training__progress">
                        <div className="show-training__progress-header">
                            <span> Step {trainingState.currentStep} / {trainingState.totalSteps}</span>
                            <span>{trainingState.progress}%</span>
                        </div>
                        <div className="show-training__progress-bar">
                            <div className="show-training__progress-fill"
                            style={{width: `${trainingState.progress}%`}}
                            />
                        </div>
                        <div className="show-training__progress-footer">
                            <span> Elapsed: {trainingState.timeElapsed}</span>
                            <span> Remaining: {trainingState.timeRemaining}</span>
                        </div>
                    </div>

                    <div className="show-training__toggle">
                        <label>
                            <input 
                                type="checkbox"
                                checked={showDetailedStats}
                                onChange={(e) => setShowDetailedStats(e.target.checked)}
                            />
                            Show detailed statistics
                        </label>
                    </div>

                    {showDetailedStats && (
                        <div className="show-training__details">
                            <div className="show-training__stat">
                                <span className="show-training__stat-label">Current Loss:</span>
                                <span className="show-training__stat-value">{trainingState.currentLoss.toFixed(4)}</span>
                            </div>

                            <div className="show-training__stat">
                                <span className="show-training__stat-label">Average Loss (last {trainingState.recentLosses.length}):</span>
                                <span className="show-training__stat-value">{trainingState.avgLoss.toFixed(4)}</span>
                            </div>
                            <div className="show-training__stat">
                                <span className="show-training__stat-label">Last Checkpoint:</span>
                                <span className="show-training__stat-value">{trainingState.lastCheckpoint}</span>
                            </div>
                            <div className="show-training__stat">
                                <span className="show-training__stat-label">Recent Losses:</span>
                                <span className="show-training__stat-value">
                                    {trainingState.recentLosses.map(l => l.toFixed(4)).join(', ')}
                                </span>
                            </div>
                        </div>
                    )}
                </> 
            )}
        </div>
    );
}

export default ShowTraining;