import { useRef } from 'react'
import server from '../../networking';
import { AlertDialog, AlertDialogBody, AlertDialogCloseButton, AlertDialogContent, AlertDialogFooter, AlertDialogHeader, AlertDialogOverlay, Button, MenuItem, Text, useDisclosure } from '@chakra-ui/react';
import { BsTrash3Fill } from 'react-icons/bs';

function DeleteFile({ fileData, triggerReload }) {
    const cancelRef = useRef(null);
    const { isOpen: isDeleteAlertOpen, onClose: onDeleteAlertClose, onOpen: onDeleteAlertOpen } = useDisclosure();

    return (
        <>
            <MenuItem color={'red'} icon={<BsTrash3Fill />} onClick={onDeleteAlertOpen}>
                Delete
            </MenuItem>
            <AlertDialog
                motionPreset='slideInBottom'
                leastDestructiveRef={cancelRef}
                onClose={onDeleteAlertClose}
                isOpen={isDeleteAlertOpen}
                isCentered
            >
                <AlertDialogOverlay />

                <AlertDialogContent>
                    <AlertDialogHeader fontSize={'md'}>Delete '{fileData.name}'?</AlertDialogHeader>
                    <AlertDialogCloseButton />
                    <AlertDialogBody>
                        <Text>Are you sure you want to delete this file? This action is irreversible.</Text>
                    </AlertDialogBody>
                    <AlertDialogFooter>
                        <Button ref={cancelRef} onClick={onDeleteAlertClose}>Cancel</Button>
                        <Button colorScheme='red' ml={3}>Confirm</Button>
                    </AlertDialogFooter>
                </AlertDialogContent>
            </AlertDialog>
        </>
    )
}

export default DeleteFile