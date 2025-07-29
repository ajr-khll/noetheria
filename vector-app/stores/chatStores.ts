import {create} from 'zustand';

type ChatState = {
    initialQuestion: string;
    setInitialQuestion: (q: string) => void;
};

export const useChatStore = create<ChatState>((set) => ({
    initialQuestion: "",
    setInitialQuestion: (q) => set({ initialQuestion: q }),
}));