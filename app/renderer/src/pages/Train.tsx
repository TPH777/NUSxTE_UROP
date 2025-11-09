import "./Train.css";
import SideBar from "../components/SideBar"
import FileInput from "../components/TableInput"
import Complete from "../components/Complete";
import ShowTraining from "../components/ShowTraining";
import Generate from "../components/Generate";
import { StageContext } from "../context/StageContext";
import { useContext, useState } from "react";


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

function Train() {

  const context = useContext(StageContext);
  const currentStage = context?.currentStage;

  const [trainingState, setTrainingState] = useState<TrainingState | null>(null);
  const [showDetailedStats, setShowDetailedStats] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<number>(Date.now());
  const [isStale, setIsStale] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [completedClasses, setCompletedClasses] = useState<number>(0);
  const [totalClasses, setTotalClasses] = useState<number>(0);

  return (
    <div className="pagesplit">
      <div className="sidebar-wrapper">
        <SideBar />
      </div>
      <div className="input-wrapper">
        { currentStage == 0 ? <FileInput /> : 
        currentStage == 1 ? <ShowTraining trainingState={trainingState} setTrainingState={setTrainingState}
          showDetailedStats={showDetailedStats} setShowDetailedStats={setShowDetailedStats} lastUpdate={lastUpdate}
          setLastUpdate={setLastUpdate} isStale={isStale} setIsStale={setIsStale} error={error} setError={setError}
          completedClasses={completedClasses} setCompletedClasses={setCompletedClasses} totalClasses={totalClasses} setTotalClasses={setTotalClasses}/> :
        currentStage == 2 ? <Generate /> : 
        <div className="complete-wrapper">
          <Complete />
        </div>
        }
      </div>
    </div>
  )
}

export default Train;