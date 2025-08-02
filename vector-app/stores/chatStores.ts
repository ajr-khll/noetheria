import {create} from 'zustand';

type ChatState = {
    initialQuestion: string;
    setInitialQuestion: (q: string) => void;
    isLoading: boolean;
    setIsLoading: (loading: boolean) => void;
    loadingMessage: string;
    setLoadingMessage: (message: string) => void;
};

export const useChatStore = create<ChatState>((set) => ({
    initialQuestion: "",
    setInitialQuestion: (q) => set({ initialQuestion: q }),
    isLoading: false,
    setIsLoading: (loading) => set({ isLoading: loading }),
    loadingMessage: "",
    setLoadingMessage: (message) => set({ loadingMessage: message }),
}));