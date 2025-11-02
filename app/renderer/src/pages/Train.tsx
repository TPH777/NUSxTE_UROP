import "./Train.css";
import SideBar from "../components/SideBar"
import FileInput from "../components/TableInput"
import Complete from "../components/Complete";
import ShowTraining from "../components/ShowTraining";
import { StageContext } from "../context/StageContext";
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
        { currentStage == 0 ? <FileInput /> : 
        currentStage == 1 ? <ShowTraining /> :
        currentStage == 2 ? 
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