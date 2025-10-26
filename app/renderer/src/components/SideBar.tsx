import "./SideBar.css";
import BarContainer from "./BarContainer";

function SideBar() {

  const stages = ["Setup", "Training", "Complete"];

  return(
    <div className="sidebar-container">
      {
        stages.map((stage, idx) => {
          return (<BarContainer idx={idx} stage={stage}/>)
        })
      }
    </div>
  )
}

export default SideBar