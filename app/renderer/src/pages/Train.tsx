import "./Train.css";
import SideBar from "../components/SideBar"
import FileInput from "../components/TableInput"

function Train() {
  return (
    <div className="pagesplit">
      <div className="sidebar-wrapper">
        <SideBar />
      </div>
      <div className="file-input-wrapper">
        <FileInput />
      </div>
    </div>
  )
}

export default Train;