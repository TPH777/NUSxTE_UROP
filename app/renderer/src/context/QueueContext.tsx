import type {ReactNode} from 'react';
import { createContext, useContext, useState } from 'react';
import { StageContext } from './StageContext.tsx';

interface QueueContextType {
  trainQueue: any[];
  generateQueue: any[];
  addTask: (task: any[], queueType: string) => void;
  taskComplete: (queueType: string) => void;
  trainQueueStarted: boolean;
  setTrainQueueStarted: React.Dispatch<React.SetStateAction<boolean>>;
  generateQueueStarted: boolean;
  setGenerateQueueStarted: React.Dispatch<React.SetStateAction<boolean>>;
}

const QueueContext = createContext<QueueContextType | undefined>(undefined);

interface QueueProviderProps {
  children: ReactNode;
}

const QueueProvider: React.FC<QueueProviderProps> = ({ children }) => {
  const [trainQueue, setTrainQueue] = useState<any[]>([]);
  const [trainQueueStarted, setTrainQueueStarted] = useState(false);
  const [generateQueue, setGenerateQueue] = useState<any[]>([]);
  const [generateQueueStarted, setGenerateQueueStarted] = useState(false);
  const stageContext = useContext(StageContext);

  const sendRequest = async (trainingParams : any, queueType: string) : Promise<any> => {
    const getApiPath = () => {
      if (queueType === "generate") {
        return "new_generate_job";
      } else if (queueType === "train") {
        return "new_training_job";
      }
      return ""
    }
    const apiPath = getApiPath();
    try {
      await fetch(`http://localhost:8000/${apiPath}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ params: trainingParams })
      });
    } catch (error) {
      console.log(error);
    }
  }

  const addTask = (task: any[], queueType: string) => {
    if (queueType === "train") {
      setTrainQueueStarted(state => {
        if (state === false) {
          return true;
        }
        return false;
      })

      setTrainQueue(prev => {
        const newList = [...prev, ...task];
        sendRequest(newList[0], queueType);
        return newList;
      });
    } else if (queueType === "generate") {
      setGenerateQueue(prev => {
        const newList = [...prev, ...task];
        sendRequest(newList[0], queueType);
        return newList;
      });
    }
  };

  const taskComplete = (queueType:string) => {
    if (queueType === "train") {
      setTrainQueue( prev => {
        const newQueue = prev.slice(1);
        if (newQueue.length === 0 && trainQueueStarted === true) {
          setTrainQueueStarted(false);
          sendRequest(generateQueue[0], "generate");
          setGenerateQueueStarted(true);
          stageContext?.setFurthestStage(2);
          stageContext?.setCurrentStage(2);
        } else {
          sendRequest(newQueue[0], queueType);
        }
        return newQueue;
      });
    } else if (queueType === "generate") {
      setGenerateQueue( prev => {
        const newQueue = prev.slice(1);
        if (newQueue.length === 0 && generateQueueStarted === true) {
          setGenerateQueueStarted(false);
          stageContext?.setFurthestStage(3);
          stageContext?.setCurrentStage(3);
        } else {
          sendRequest(newQueue[0], queueType);
        }
        return newQueue;
      });
    }
  }

  return (
    <QueueContext.Provider value={{ trainQueue, generateQueue, addTask, taskComplete, 
        trainQueueStarted, setTrainQueueStarted, generateQueueStarted, setGenerateQueueStarted }}>
      {children}
    </QueueContext.Provider>
  );
};

export {QueueProvider, QueueContext};
