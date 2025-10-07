import "./Background.css";
import logo from "../assets/Logo.png";
import { Link } from 'react-router-dom';
import type React from "react";
function Background() {
  return (
    <div className="door-container">
      {/*<div className="card-container">

      </div>
      <div className="glow-dot"></div>*/}
      <div className="logo-container">
        <img src={logo} className="logo"></img>
      </div>
      <Link to='/train'>
        <button></button>
      </Link>
      <div className="door door-top">
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

      <div className="door door-bottom">
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

      <div className="center-seam"></div>
    </div>

  )
}

export default Background;
