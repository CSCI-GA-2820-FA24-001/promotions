const StateManager = (() => {
    /** @type {'start_date' | 'end_date'|'date_range'|null} */
    const state = {
        dateType: null
    };

    return {
        getDateType: () => {
            return state.dateType;
        },
        setDateType: (newType) => {
            state.dateType = newType;
            console.log('Date Type updated to:', state.dateType);
        }
    };
})();
