import "./BarContainer.css";
import { useContext } from 'react';
import { StageContext } from '../context/stageContext';

type BarContainerProps = {
  idx: number;
  stage: string;
}

const BarContainer : React.FC<BarContainerProps> = ({idx, stage}) => {

  const context = useContext(StageContext);
  const currentStage = context?.currentStage;

  return (
    <div className= {idx == currentStage ? "bar-container selected" : "bar-container"}>
      <p className={ idx == currentStage ? "stageFront selected" : "stageFont"}>{stage}</p>
    </div>
  )
}

export default BarContainer