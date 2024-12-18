import { createSlice } from '@reduxjs/toolkit';
import server from '../networking';

const initialState = {
    accountID: null,
    username: null,
    loaded: false,
    error: null,
    disableSessionCheck: false,
}

const authSlice = createSlice({
    name: 'auth',
    initialState,
    reducers: {
        setAccountID: (state, action) => {
            state.accountID = action.payload;
        },
        setUsername: (state, action) => {
            state.username = action.payload;
        },
        setLoaded: (state, action) => {
            state.loaded = action.payload;
        },
        setError: (state, action) => {
            state.error = action.payload;
        },
        setDisableSessionCheck: (state, action) => {
            state.disableSessionCheck = action.payload;
        },
        stateLogout: (state) => {
            state.accountID = null;
            state.username = null;
            state.error = null;
        }
    },
});

export const retrieveSession = async () => {
    try {
        const response = await server.get('/identity/session');
        if (!response.data || !response.data.session) {
            throw new Error('Invalid response: ' + JSON.stringify(response.data));
        }
        return response.data.session;
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

export const { setAccountID, setUsername, setLoaded, setError, setDisableSessionCheck, stateLogout } = authSlice.actions;

export const fetchSession = (handler=null) => async (dispatch) => {
    // console.log('Fetching session...');
    dispatch(setLoaded(false));
    const response = await retrieveSession();
    if (response.aID && response.username) {
        dispatch(setAccountID(response.aID));
        dispatch(setUsername(response.username));
    } else {
        dispatch(setError(response.error));
    }
    dispatch(setLoaded(true));
    
    if (handler) {
        handler(response);
    }
};

export const logout = (disableSessionCheck=false, handler=null) => async (dispatch) => {
    try {
        const response = await server.get('/identity/logout')
        if (response.status === 200 && typeof response.data == "string" && response.data.startsWith("SUCCESS")) {
            if (disableSessionCheck) {
                dispatch(setDisableSessionCheck(true));
            }
            dispatch(stateLogout());
        } else {
            console.log("Unexpected response in logout; response:", response.data);
        }

        if (handler) {
            handler(response.data);
        }
    } catch (err) {
        var e = null;
        if (err.response && err.response.data && typeof err.response.data === 'string') {
            e = err.response.data;
        } else if (err.message && typeof err.message === 'string') {
            e = "ERROR: " + err.message;
        } else if (typeof err === 'string') {
            e = "ERROR: " + err;
        } else {
            e = 'ERROR: An unknown error occurred.';
        }

        console.log("Error in logout:", e);

        if (handler) {
            handler(e);
        }
    }
}

export default authSlice.reducer;