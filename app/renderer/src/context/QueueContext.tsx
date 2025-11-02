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

  const addTask = (task: any[]) => {
    setQueueStarted(state => {
      if (state === false) {
        return true;
      }
      return false;
    })
    setQueue(prev => {
      const newList = [...prev, ...task]
      // calls the first train with the first param
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
        // call the next training
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
