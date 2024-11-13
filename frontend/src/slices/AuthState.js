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

export const retrieveSession = async () => {
    try {
        const response = await server.get('/identity/session');
        if (!response.data || !response.data.username) {
            throw new Error('Invalid response: ' + JSON.stringify(response.data));
        }
        return { username: response.data.username };
    } catch (err) {
        var e = null;
        if (err.response && err.response.data && typeof err.response.data === 'string') {
            e = err.response.data;
        } else if (err.message && typeof err.message === 'string') {
            e = err.message;
        } else if (typeof err === 'string') {
            e = err;
        } else {
            e = 'An unknown error occurred.';
        }

        console.log("Error fetching session:", e);

        return { error: e };
    }
}

export const { setUsername, setLoaded, setError } = authSlice.actions;

export const fetchSession = () => async (dispatch) => {
    // console.log('Fetching session...');
    dispatch(setLoaded(false));
    const response = await retrieveSession();
    if (response.username) {
        dispatch(setUsername(response.username));
    } else {
        dispatch(setError(response.error));
    }
};

export default authSlice.reducer;