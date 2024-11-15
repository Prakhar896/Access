import { useSelector } from "react-redux";
import { useNavigate } from "react-router-dom"
import CentredSpinner from "./CentredSpinner";
import { useEffect } from "react";
import { useToast } from "@chakra-ui/react";
import configureShowToast from "./showToast";

const withAuth = (WrappedComponent) => {
    return (props) => {
        const navigate = useNavigate();
        const toast = useToast();
        const showToast = configureShowToast(toast);
        const { username, loaded, error } = useSelector(state => state.auth);

        useEffect(() => {
            if (!username && loaded) {
                navigate('/login');
                showToast("Please sign in first", '', 'error');
                console.log('Unauthorised access detected; redirecting.');
            }
        }, [username, loaded])

        if (!loaded) {
            return <CentredSpinner />
        }

        return <WrappedComponent {...props} />
    }
}

export default withAuth;