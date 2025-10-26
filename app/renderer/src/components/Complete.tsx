import React from "react";
import "./Complete.css";
import tick from "../assets/orange-tick.png";

const Complete: React.FC = () => {
  return(
    <div className="complete-wrapper">
      <img src={tick} className="tick"></img>
      <p className="complete-msg">Generation Complete!</p>
      <p className="saved-msg">Images are saved to ...</p>
      <div className="complete-button-container">
        <button className="complete-button">Complete</button>
      </div>
    </div>
  )
}

export default Complete;