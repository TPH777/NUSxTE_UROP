import "./BarContainer.css";

type BarContainerProps = {
  stage: string;
}

function BarContainer({stage} : BarContainerProps) {
  return (
    <div className="bar-container selected">
      <p className="stageFont selected">{stage}</p>
    </div>
  )
}

export default BarContainer