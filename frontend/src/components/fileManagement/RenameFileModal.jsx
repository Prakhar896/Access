import { useEffect, useRef, useState } from 'react'
import { Button, FormControl, FormHelperText, FormLabel, HStack, Input, MenuItem, Modal, ModalBody, ModalCloseButton, ModalContent, ModalFooter, ModalHeader, ModalOverlay, Text, useDisclosure, useToast } from '@chakra-ui/react'
import { BsPencilFill } from 'react-icons/bs'
import configureShowToast from '../showToast';
import server from '../../networking';

function RenameFileModal({ fileData, renameModalOpen, onRenameModalOpen, onRenameModalClose, triggerReload }) {
    const initialRef = useRef(null);
    const toast = useToast();
    const showToast = configureShowToast(toast);

    const [newFilename, setNewFilename] = useState('');
    const [renaming, setRenaming] = useState(false);

    const handleRenameInputEnter = (e) => { if (e.key === 'Enter') renameFile() };
    const handleRenameInputChange = (e) => { setNewFilename(e.target.value) };
    const handleRenameClose = () => {
        setNewFilename('');
        setRenaming(false);
        onRenameModalClose();
    }

    const renameDisabled = renaming || newFilename.trim().length <= 0;

    const renameFile = () => {
        const newName = newFilename.trim();
        if (newName.length <= 0) {
            showToast("Filename must not be empty", '', 'error');
            return
        }
        if (newName === fileData.name) {
            showToast("New filename must be different", '', 'error');
            return
        }
        if (!/^[a-zA-Z0-9_\- ]+\.[a-zA-Z]+$/.test(newName)) {
            showToast("Invalid filename", "Filename must be alphanumeric with underscores, hyphens, and spaces only, and must have a file extension.", "error");
            return
        }

        const originalFileExtension = fileData.name.split('.')[fileData.name.split('.').length - 1];
        const newFileExtension = newName.split('.')[newName.split('.').length - 1];
        if (originalFileExtension !== newFileExtension) {
            if (!confirm("Changing the file extension may cause the file to be unreadable. Are you sure you want to continue?")) {
                return
            }
        }

        setRenaming(true);
        server.post("/directory/renameFile", {
            filename: fileData.name,
            newFilename: newName
        })
            .then(res => {
                if (res.status == 200) {
                    if (typeof res.data == "string" && res.data.startsWith("SUCCESS")) {
                        showToast("File renamed!", '', 'success');
                        handleRenameClose();

                        if (triggerReload) {
                            triggerReload();
                        }
                        return
                    } else {
                        console.log(`Unexpected response when renaming file '${fileData.name}'; response: ${res.data}`);
                        showToast("Something went wrong", "Couldn't rename file. Please try again.", "error");
                    }
                } else {
                    console.log(`Non-200 status code response received when renaming file '${fileData.name}'; response: `, res.data);
                    showToast("Something went wrong", "Couldn't rename file. Please try again.", "error");
                }

                setRenaming(false);
            })
            .catch(err => {
                if (err.response && err.response.data && typeof err.response.data == "string") {
                    if (err.response.data.startsWith("UERROR")) {
                        console.log(`User error occurred when renaming file '${fileData.name}'; response: ${err.response.data}`);
                        showToast("Something went wrong", err.response.data.substring("UERROR: ".length), "error");
                        setRenaming(false);
                        return
                    } else {
                        console.log(`Error when renaming file '${fileData.name}'; response: ${err.response.data}`);
                    }
                } else if (err.message && typeof err.message == "string") {
                    console.log(`Error occurred when renaming file '${fileData.name}'; message: ${err.message}`);
                } else {
                    console.log(`Unknown error occurred when renaming file '${fileData.name}'; error: ${err}`);
                }

                showToast("Something went wrong", "Couldn't rename file. Please try again.", "error");
                setRenaming(false);
            })
    }

    useEffect(() => {
        if (fileData && fileData.name) {
            setNewFilename(fileData.name)
        } else {
            handleRenameClose();
        }
    }, [fileData])

    return (
        <Modal onClose={handleRenameClose} isOpen={renameModalOpen} initialFocusRef={initialRef} isCentered>
            <ModalOverlay />
            <ModalContent>
                <ModalHeader>Rename File</ModalHeader>
                {!renaming && <ModalCloseButton />}
                <ModalBody>
                    <Text>Original name: {fileData.name}</Text>
                    <FormControl mt={"10px"}>
                        <FormLabel fontFamily={'Ubuntu'}>Enter new filename</FormLabel>
                        <Input ref={initialRef} type='text' name='newFilename' id='newFilename' placeholder='e.g NewName.pdf' isDisabled={renaming} value={newFilename} onChange={handleRenameInputChange} onKeyDown={handleRenameInputEnter} />
                        <FormHelperText fontFamily={'Ubuntu'}>Must be a valid name with file extension and should not already exist.</FormHelperText>
                    </FormControl>
                </ModalBody>
                <ModalFooter>
                    <HStack spacing={"10px"}>
                        {!renaming && (
                            <Button variant={'ghost'} onClick={handleRenameClose}>Cancel</Button>
                        )}
                        <Button variant={!renaming ? 'Default' : 'solid'} onClick={renameFile} isDisabled={renameDisabled} isLoading={renaming} loadingText={"Renaming..."}>Rename</Button>
                    </HStack>
                </ModalFooter>
            </ModalContent>
        </Modal>
    )
}

export default RenameFileModal