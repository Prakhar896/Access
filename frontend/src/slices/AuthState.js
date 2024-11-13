import { createSlice } from '@reduxjs/toolkit';
import server from '../networking';

const initialState = {
    username: null,
    loaded: false,
    error: null
}

const authSlice = createSlice({
    name: 'auth',
    initialState,
    reducers: {
        setUsername: (state, action) => {
            state.username = action.payload;
        },
        setLoaded: (state, action) => {
            state.loaded = action.payload;
        },
        setError: (state, action) => {
            state.error = action.payload;
        }
    },
});

export const { setUsername, setLoaded, setError } = authSlice.actions;

export const fetchSession = () => async (dispatch) => {
    console.log('Fetching session...');
    dispatch(setLoaded(false));
    try {
        const response = await server.get('/identity/session');
        if (!response.data || !response.data.username) {
            throw new Error('Invalid response: ' + JSON.stringify(response.data));
        }
        dispatch(setUsername(response.data.username));
        dispatch(setLoaded(true));
    } catch (err) {
        console.log('Error fetching session:', err);
        if (err.response && err.response.data && typeof err.response.data === 'string') {
            dispatch(setError(err.response.data));
        } else if (err.message && typeof err.message === 'string') {
            dispatch(setError(err.message));
        } else if (typeof err === 'string') {
            dispatch(setError(err));
        } else {
            dispatch(setError('An unknown error occurred.'));
        }
        dispatch(setLoaded(true));
    }
};

export default authSlice.reducer;