import type { ReactNode } from 'react';
import { createContext, useState} from 'react';

interface StageContextType {
  currentStage: number;
  setCurrentStage: React.Dispatch<React.SetStateAction<number>>;
}

const StageContext = createContext<StageContextType | undefined>(undefined);

interface StageProviderProps {
  children: ReactNode;
}

const StageProvider: React.FC<StageProviderProps> = ({children}) => {
  const [currentStage, setCurrentStage] = useState<number>(3);

  return (
    <StageContext.Provider value={{ currentStage, setCurrentStage}}>
      {children}
    </StageContext.Provider>
  );
};

export { StageContext, StageProvider };