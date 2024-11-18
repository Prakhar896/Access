import { useSelector } from "react-redux";
import { useNavigate } from "react-router-dom"
import CentredSpinner from "../CentredSpinner";
import { useEffect } from "react";
import { Box, Fade, Spinner, useToast } from "@chakra-ui/react";
import configureShowToast from "../showToast";
import { AnimatePresence, motion } from "framer-motion";

const MotionBox = motion(Box);

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

        return (
            <AnimatePresence mode="wait">
                {!loaded ? (
                    <MotionBox
                        key="spinner"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0, transition: { duration: 0.1 } }}
                    >
                        <CentredSpinner />
                    </MotionBox>
                ) : (
                    <MotionBox
                        key="content"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1, transition: { duration: 0.1 } }}
                        exit={{ opacity: 0 }}
                    >
                        <WrappedComponent {...props} />
                    </MotionBox>
                )}
            </AnimatePresence>
        );
    }
}

export default withAuth;