import {useContext, useEffect} from 'react';
import './ShowTraining.css'
import { QueueContext } from '../context/QueueContext';

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
    currentClass: number;
    totalClasses: number;
    isComplete: boolean;
}

type ShowTrainingVar = {
  trainingState: TrainingState | null,
  setTrainingState: React.Dispatch<React.SetStateAction<TrainingState | null>>,
  showDetailedStats: boolean,
  setShowDetailedStats: React.Dispatch<React.SetStateAction<boolean>>,
  lastUpdate: number,
  setLastUpdate: React.Dispatch<React.SetStateAction<number>>,
  isStale: boolean,
  setIsStale: React.Dispatch<React.SetStateAction<boolean>>,
  error: string | null,
  setError: React.Dispatch<React.SetStateAction<string | null>>
  completedClasses: number,
  setCompletedClasses: React.Dispatch<React.SetStateAction<number>>,
  totalClasses: number,
  setTotalClasses: React.Dispatch<React.SetStateAction<number>>,
}

declare global {
    interface Window {
        require: ((module: string) => any) | undefined;
    }
}

const ShowTraining: React.FC<ShowTrainingVar> = ({trainingState, setTrainingState, showDetailedStats, setShowDetailedStats,
  lastUpdate, setLastUpdate, isStale, setIsStale, error, setError, completedClasses, 
  setCompletedClasses, totalClasses, setTotalClasses
} ) => {

    const queueContext = useContext(QueueContext);

    useEffect(() => {
        
        const loadTotalClasses = async () => {
            try {
                if (!window.require) return;
        
                const electron = window.require('electron') as any;
                const { ipcRenderer } = electron;
                const result = await ipcRenderer.invoke('read-training-queue');

                if (result.success) {
                    setTotalClasses(result.totalClasses);
                    console.log('Total classes to train:', result.totalClasses);
                }
            } catch (err) {
                console.error('Failed to read training queue:', err);
            }
        };
        loadTotalClasses();

        const pollInterval = 5000 // 5 seconds
        const staleThreshold = pollInterval * 12 // 1 minute - consider stale if no update

        const readTrainingLog = async () => {
            try {
                // Use IPC to read file from main process
                if (!window.require) return;
        
                const electron = window.require('electron') as any;
                const { ipcRenderer } = electron;
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

                    if (parsed.isComplete) {
                        console.log('Class Training Completed!');
                        setCompletedClasses(prev => {
                            const newCount = prev + 1;
                            console.log(`Completed ${newCount}/${totalClasses} classes`);

                            if (newCount >= totalClasses) {
                                console.log('All training completed!')
                                return newCount;
                            }

                            return newCount;
                        });

                        if (completedClasses + 1 < totalClasses) {
                            const electron = window.require('electron') as any;
                            const { ipcRenderer } = electron;
                            await ipcRenderer.invoke('clear-training-log');
                            console.log('Log file cleared, ready for next class');
                        }
                    }
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
        let isComplete = false;

        const completionPattern = /Complete Training For ['"](.+?)['"]/;

        //process lines from end
        for (let i = lines.length - 1; i >= 0 && recentLosses.length < 5; i--) {
            const line = lines[i];

            if (completionPattern.test(line)) {
                isComplete = true;
                queueContext?.taskComplete("train");
                console.log('Detected training completion:', line);
            }

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
            currentClass: completedClasses + 1,
            totalClasses: totalClasses,
            isComplete,
        } as TrainingState;
    };

    return (
        <div className="show-training">
            <h2> Training Progress</h2>

            {totalClasses > 0 && completedClasses < totalClasses && (
                <div className="show-training__class-counter">
                    Trained: {completedClasses} / {totalClasses} classes
                </div>
            )}

            {totalClasses > 0 && completedClasses >= totalClasses && (
                <div className="show-training__class-counter show-training__class-counter--complete">
                    ✓ Training Completed - Proceed to Generate
                </div>
            )}

            {error && error.includes('File is empty') && completedClasses < totalClasses && (
                <div className="show-training__info">
                    Training completed for class {completedClasses}. Moving on to next class...
                </div>
            )}

            {error && !error.includes('File is empty') && (
                <div className="show-training__error"> 
                    {error}
                </div>
            )}

            {isStale && trainingState && (
                <div className="show-training__warning">
                    Training appears to have stopped. Last update: {Math.floor((Date.now() - lastUpdate) / 1000)}s ago
                </div>
            )}

            {!trainingState && !error && completedClasses < totalClasses && (
                <div className="show-training__empty">
                    Waiting for training to start...
                </div>
            )}

            {!trainingState && !error && (
                <div className="show-training__empty">
                    Waiting for training to start...
                </div>
            )}

            {trainingState && completedClasses < totalClasses && (

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