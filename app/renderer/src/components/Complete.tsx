import React from "react";
import "./Complete.css";
import tick from "../assets/orange-tick.png";
import { StageContext } from "../context/StageContext";
import { useContext } from "react";

const Complete: React.FC = () => {
  const context = useContext(StageContext);

  const resetStages = (): void => {
    context?.setCurrentStage(0);
    context?.setFurthestStage(0);
  }

  return(
    <div className="complete-wrapper">
      <img src={tick} className="tick"></img>
      <p className="complete-msg">Generation Complete!</p>
      <p className="saved-msg">Images are saved to ...</p>
      <div className="complete-button-container" onClick={() => {resetStages()}}>
        <button className="complete-button">Complete</button>
      </div>
    </div>
  )
}

export default Complete;