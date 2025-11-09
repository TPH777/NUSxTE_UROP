import "./Background.css";
import logo from "../assets/Logo.png";
import { useNavigate } from 'react-router-dom';
import { useState } from "react";
function Background() {

  const [doorOpen, setDoorOpen] = useState(false);
  const [passwordInfo, setPasswordInfo] = useState("")
  const [usernameInfo, setUsernameInfo] = useState("")

  const navigate = useNavigate();

  const openDoor = () => {
    setDoorOpen(true);
    setTimeout(() => {
      navigate('/train');
    }, 3200);
  }

  return (
    <div className="door-container">
      <div className={doorOpen ? "card-container disappear" : "card-container"}>
        <div>
          <p className="large-font font-orange">Welcome back</p>
          <p className="small-font no-margin font-orange">Please log in to continue</p>
        </div>
        <input
          type="text"
          value={usernameInfo}
          onChange={(e) => setUsernameInfo(e.target.value)}
          placeholder="Username"
          className="text-input font-white"
        /> 
        <input
          type="password"
          value={passwordInfo}
          onChange={(e) => setPasswordInfo(e.target.value)}
          placeholder="Password"
          className="text-input font-off-white"
        /> 
        <button className="button font-white" onClick={openDoor}>Login</button>
      </div>
      <div className={doorOpen ? "glow-dot disappear" : "glow-dot"}></div>
      <div className={doorOpen ? "logo-container disappear" : "logo-container"}>
        <img src={logo} className="logo"></img>
      </div>
      <div className={doorOpen ? "door door-top slide-up" : "door door-top"}>
        <div className="door-details">
          <div className="door-lines">
            <div className="line horizontal line-top"></div>
            <div className="line horizontal line-bottom"></div>
            <div className="line vertical"></div>
          </div>

          <div className="rivet rivet-top-left"></div>
          <div className="rivet rivet-top-right"></div>
        </div>
      </div>

      <div className={doorOpen ? "door door-bottom slide-down" : "door door-bottom"}>
        <div className="door-details">
          <div className="door-lines">
            <div className="line horizontal line-top"></div>
            <div className="line horizontal line-bottom"></div>
            <div className="line vertical"></div>
          </div>

          <div className="rivet rivet-bottom-left"></div>
          <div className="rivet rivet-bottom-right"></div>
        </div>
      </div>

      <div className={doorOpen ? "center-seam disappear" : "center-seam"}></div>
    </div>

  )
}

export default Background;
