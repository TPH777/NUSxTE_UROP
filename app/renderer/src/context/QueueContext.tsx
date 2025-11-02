import type {ReactNode} from 'react';
import { createContext, useContext, useState } from 'react';
import { StageContext } from './StageContext.tsx';

interface QueueContextType {
  queue: any[];
  addTask: (task: any[]) => void;
  taskComplete: () => void;
  queueStarted: boolean;
  setQueueStarted: React.Dispatch<React.SetStateAction<boolean>>;
}

const QueueContext = createContext<QueueContextType | undefined>(undefined);

interface QueueProviderProps {
  children: ReactNode;
}

const QueueProvider: React.FC<QueueProviderProps> = ({ children }) => {
  const [queue, setQueue] = useState<any[]>([]);
  const [queueStarted, setQueueStarted] = useState(false);
  const stageContext = useContext(StageContext);

  const sendTrainRequest = async (trainingParams : any) : Promise<any> => {
    try {
      await fetch('http://localhost:8000/new_generate_job', {
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

  const addTask = (task: any[]) => {
    setQueueStarted(state => {
      if (state === false) {
        return true;
      }
      return false;
    })

    setQueue(prev => {
      const newList = [...prev, ...task];
      sendTrainRequest(newList[0]);
      return newList;
    });
  };

  const taskComplete = () => {
    setQueue( prev => {
      const newQueue = prev.slice(1);
      if (newQueue.length === 0 && queueStarted === true) {
        setQueueStarted(false);
        stageContext?.setFurthestStage(2);
        stageContext?.setCurrentStage(2);
      } else {
        sendTrainRequest(newQueue[0]);
      }
      return newQueue;
    });
    
  }

  return (
    <QueueContext.Provider value={{ queue, addTask, taskComplete, queueStarted, setQueueStarted }}>
      {children}
    </QueueContext.Provider>
  );
};

export {QueueProvider, QueueContext};
