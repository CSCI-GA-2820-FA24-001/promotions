const StateManager = (() => {
    /** 
     * @type {{dateType: 'start_date' | 'end_date' | 'date_range' | null, creator: string | null, updater: string | null}}
     */
    const state = {
        dateType: null,
        creator: null,
        updater: null
    };

    return {
        getDateType: () => {
            return state.dateType;
        },
        setDateType: (newType) => {
            state.dateType = newType;
            console.log('Date Type updated to:', state.dateType);
        },
        getCreator: () => {
            return state.creator;
        },
        setCreator: (newCreator) => {
            state.creator = newCreator;
            console.log('Creator updated to:', state.creator);
        },
        getUpdater: () => {
            return state.updater;
        },
        setUpdater: (newUpdater) => {
            state.updater = newUpdater;
            console.log('Updater updated to:', state.updater);
        }
    };
})();
