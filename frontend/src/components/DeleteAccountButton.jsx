import { AlertDialog, AlertDialogBody, AlertDialogCloseButton, AlertDialogContent, AlertDialogFooter, AlertDialogHeader, AlertDialogOverlay, Button, Text, useDisclosure, useMediaQuery, useToast } from '@chakra-ui/react'
import { useRef, useState } from 'react'
import server from '../networking';
import configureShowToast from './showToast';
import { useNavigate } from 'react-router-dom';
import { setDisableSessionCheck, stateLogout } from '../slices/AuthState';
import { useDispatch } from 'react-redux';
import { FaWaveSquare } from 'react-icons/fa';

function DeleteAccountButton() {
    const [limitedScreen] = useMediaQuery("(max-width: 800px)");
    const { isOpen: isDeleteAccountModalOpen, onOpen: onDeleteAccountModalOpen, onClose: onDeleteAccountModalClose } = useDisclosure();
    const cancelRef = useRef();
    const [deleting, setDeleting] = useState(false);

    const navigate = useNavigate();
    const dispatch = useDispatch();
    const toast = useToast();
    const showToast = configureShowToast(toast);

    const deleteAccount = async () => {
        setDeleting(true);
        server.post("/profile/delete")
            .then(res => {
                if (res.status == 200) {
                    if (typeof res.data == "string" && res.data.startsWith("SUCCESS")) {
                        console.log(res.data);
                        showToast("Account Deleted.", res.data.substring("SUCCESS: ".length), "success", 10000, true, <Text>👋</Text>);
                        setDeleting(false);
                        onDeleteAccountModalClose();
                        dispatch(setDisableSessionCheck(true));
                        dispatch(stateLogout());
                        navigate('/');
                        return
                    } else {
                        console.log("Unexpected response in deleting account; response:", res.data);
                    }
                } else {
                    console.log("Non-200 status code in deleting account; response:", res.data);
                }

                showToast("Something went wrong", "Couldn't delete account. Please try again.", "error");
                setDeleting(false);
            })
            .catch(err => {
                if (err.response && err.response.data && typeof err.response.data == "string") {
                    if (err.response.data.startsWith("UERROR")) {
                        console.log("User error occurred in deleting account; response:", err.response.data);
                        showToast("Something went wrong", err.response.data.substring("UERROR: ".length), "error");
                        setDeleting(false);
                        return
                    } else {
                        console.log("Error occurred in deleting account; response:", err.response.data);
                    }
                } else if (err.message && typeof err.message == "string") {
                    console.log("Error occurred in deleting account; error:", err.message);
                } else {
                    console.log("Unknown error occurred in deleting account; error:", err);
                }

                showToast("Something went wrong", "Couldn't delete account. Please try again.", "error");
                setDeleting(false);
            })
    }

    return (
        <>
            <Button mt={"30px"} mb={"20px"} maxW={limitedScreen ? "100%" : "fit-content"} colorScheme='red' variant={'outline'} onClick={onDeleteAccountModalOpen}>Delete Identity</Button>
            <AlertDialog
                motionPreset='slideInBottom'
                leastDestructiveRef={cancelRef}
                onClose={onDeleteAccountModalClose}
                isOpen={isDeleteAccountModalOpen}
                size={{ base: 'md', md: 'lg', lg: 'xl' }}
                isCentered
            >
                <AlertDialogOverlay />

                <AlertDialogContent>
                    <AlertDialogHeader>Confirm delete?</AlertDialogHeader>
                    {!deleting && <AlertDialogCloseButton />}
                    <AlertDialogBody>
                        <Text fontWeight={'black'}>Are you sure you want to delete your Access Identity?</Text>
                        <Text mt={"10px"}>This will delete all account-related resources like audit logs and files, which cannot be recovered. Please take caution before continuing.</Text>
                    </AlertDialogBody>
                    <AlertDialogFooter>
                        {!deleting ? (
                            <Button ref={cancelRef} onClick={onDeleteAccountModalClose}>
                                Cancel
                            </Button>
                        ) : (
                            <Text fontSize={'sm'}>This may take a few moments...</Text>
                        )}
                        <Button colorScheme='red' variant={'solid'} ml={3} onClick={deleteAccount} isLoading={deleting} loadingText={"Deleting..."}>
                            Delete
                        </Button>
                    </AlertDialogFooter>
                </AlertDialogContent>
            </AlertDialog>
        </>
    )
}

export default DeleteAccountButton