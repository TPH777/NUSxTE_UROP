import "./BarContainer.css";
import { useContext } from 'react';
import { StageContext } from '../context/stageContext';

type BarContainerProps = {
  idx: number;
  stage: string;
}

const BarContainer : React.FC<BarContainerProps> = ({idx, stage}) => {

  const context = useContext(StageContext);
  const currentStage = context?.currentStage ?? -1;
  const furthestStage = context?.furthestStage ?? -1;

  return (
    <div className= {idx == currentStage ? "bar-container selected" : idx <= furthestStage ? "bar-container clickable" : "bar-container"} 
    onClick={() => {context?.setCurrentStage(idx)}}>
      <p className={ idx == currentStage ? "stageFront selected" : idx <= furthestStage ? "stageFont clickable" : "stageFont"}>{stage}</p>
    </div>
  )
}

export default BarContainer