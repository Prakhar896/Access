import { useRef, useState } from 'react'
import server from '../../networking';
import { AlertDialog, AlertDialogBody, AlertDialogCloseButton, AlertDialogContent, AlertDialogFooter, AlertDialogHeader, AlertDialogOverlay, Button, MenuItem, Text, useDisclosure, useToast } from '@chakra-ui/react';
import { BsTrash3Fill } from 'react-icons/bs';
import configureShowToast from '../showToast';

function DeleteFileModal({ fileData, isDeleteAlertOpen, onDeleteAlertOpen, onDeleteAlertClose, triggerReload }) {
    const cancelRef = useRef(null);
    const toast = useToast();
    const showToast = configureShowToast(toast);

    const [deleting, setDeleting] = useState(false);

    const handleDeleteClose = () => {
        setDeleting(false);
        onDeleteAlertClose();
    }

    const deleteFile = () => {
        setDeleting(true);

        server.delete("/directory/file", {
            data: {
                filenames: fileData.name
            }
        })
            .then(res => {
                if (res.status == 200) {
                    if (typeof res.data == "string" && res.data.startsWith("SUCCESS")) {
                        showToast("File deleted!", '', 'success');
                        handleDeleteClose();

                        if (triggerReload) {
                            triggerReload()
                        }
                        return;
                    } else {
                        console.log(`Unexpected response in deleting file '${fileData.name}'; response:`, res.data)
                    }
                } else {
                    console.log(`Non-200 status code response in deleting file '${fileData.name}'; response:`, res.data);
                }

                showToast("Something went wrong", "Couldn't delete file. Please try again.", 'error');
                setDeleting(false);
            })
            .catch(err => {
                if (err.response && err.response.data && typeof err.response.data == "string") {
                    if (err.response.data.startsWith("UERROR")) {
                        console.log(`User error occurred in deleting file '${fileData.name}'; response:`, err.response.data);
                        showToast("Something went wrong", err.response.data.substring("UERROR: ".length), 'error');
                        setDeleting(false);
                        return;
                    } else {
                        console.log(`Unexpected response in deleting file '${fileData.name}'; response:`, err.response.data);
                    }
                } else if (err.message && typeof err.message == "string") {
                    console.log(`Error in deleting file '${fileData.name}'; message:`, err.message);
                } else {
                    console.log(`Unknown error in deleting file '${fileData.name}'; error:`, err);
                }

                showToast("Something went wrong", "Couldn't delete file. Please try again.", 'error');
                setDeleting(false);
            })
    }

    return (
        <AlertDialog
            motionPreset='slideInBottom'
            leastDestructiveRef={cancelRef}
            onClose={handleDeleteClose}
            isOpen={isDeleteAlertOpen}
            isCentered
        >
            <AlertDialogOverlay />

            <AlertDialogContent>
                <AlertDialogHeader>Delete '{fileData.name}'?</AlertDialogHeader>
                <AlertDialogBody>
                    <Text>Are you sure you want to delete this file? This action is irreversible.</Text>
                </AlertDialogBody>
                <AlertDialogFooter>
                    {!deleting && <Button ref={cancelRef} onClick={handleDeleteClose}>Cancel</Button>}
                    <Button colorScheme='red' ml={3} onClick={deleteFile} isLoading={deleting} loadingText={"Deleting..."}>Delete</Button>
                </AlertDialogFooter>
            </AlertDialogContent>
        </AlertDialog>
    )
}

export default DeleteFileModal