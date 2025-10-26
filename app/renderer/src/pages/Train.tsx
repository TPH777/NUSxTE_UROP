import "./Train.css";
import SideBar from "../components/SideBar"
import FileInput from "../components/TableInput"
import Complete from "../components/Complete";
import { StageContext } from "../context/stageContext";
import { useContext } from "react";

function Train() {

  const context = useContext(StageContext);
  const currentStage = context?.currentStage;

  return (
    <div className="pagesplit">
      <div className="sidebar-wrapper">
        <SideBar />
      </div>
      <div className="input-wrapper">
        { currentStage == 0 ? 
        <FileInput /> : currentStage == 1 || currentStage == 2 ? 
        <div>
        </div> : 
        <div className="complete-wrapper">
          <Complete />
        </div>
        }
      </div>
    </div>
  )
}

export default Train;