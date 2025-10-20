import React, { createContext, useContext, useState, ReactNode } from 'react';

interface SearchResults {
    query: string;
    responses: {
        opensource: string;
        lawgpt: string;
        proprietary: string;
    };
}

interface AgenticResult {
    type: 'search' | 'navigation' | 'profile_update' | 'settings_update' | 'theme_change' | 'help' | 'error';
    data: any;
    message: string;
}

interface SearchContextType {
    searchResults: SearchResults | null;
    setSearchResults: (results: SearchResults | null) => void;
    agenticResult: AgenticResult | null;
    setAgenticResult: (result: AgenticResult | null) => void;
}

const SearchContext = createContext<SearchContextType | undefined>(undefined);

export const SearchProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    const [searchResults, setSearchResults] = useState<SearchResults | null>(null);
    const [agenticResult, setAgenticResult] = useState<AgenticResult | null>(null);

    return (
        <SearchContext.Provider value={{ searchResults, setSearchResults, agenticResult, setAgenticResult }}>
            {children}
        </SearchContext.Provider>
    );
};

export const useSearch = () => {
    const context = useContext(SearchContext);
    if (context === undefined) {
        throw new Error('useSearch must be used within a SearchProvider');
    }
    return context;
};
