import { Box, Button, Card, FormControl, FormLabel, HStack, Input, Modal, ModalBody, ModalCloseButton, ModalContent, ModalFooter, ModalHeader, ModalOverlay, Text, useDisclosure, useToast } from '@chakra-ui/react'
import React, { useEffect, useState } from 'react'
import UploadFileCard from './UploadFileCard';
import server from '../networking';
import configureShowToast from './showToast';

function UploadFilesModal({ isOpen, onClose, onOpen, triggerReload }) {
    const toast = useToast();
    const showToast = configureShowToast(toast);

    const [files, setFiles] = useState([]);
    const [fileUploadResults, setFileUploadResults] = useState({});
    const [uploading, setUploading] = useState(false);

    const handleFileChange = (event) => {
        const files = Array.from(event.target.files);
        setFiles((prevFiles) => [...prevFiles, ...files]);
    };

    const handleRemoveFile = (index) => {
        setFiles((prevFiles) => prevFiles.filter((_, fileIndex) => fileIndex !== index));
    };

    const handleUpload = async () => {
        setUploading(true);
        setFileUploadResults({});

        const formData = new FormData();
        files.forEach((file) => {
            formData.append("file", file);
        })

        try {
            const response = await server.post("/directory", formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                },
                transformRequest: formData => formData
            })

            if (response.status == 200 && typeof response.data == "object" && !Array.isArray(response.data)) {
                setFileUploadResults(response.data);
            } else {
                console.log("Unexpected response format or non-200 code when uploading files; response: ", response.data);
                showToast("Something went wrong", "Couldn't upload files. Please try again.", "error");
            }

            setUploading(false);
            if (triggerReload) {
                triggerReload();
            }
        } catch (err) {
            if (err.response && err.response.status && err.response.status == 413) {
                console.log("File too large error occurred when uploading files; response: ", err.response.data);
                showToast("Something went wrong", "One or more files are too large. Please try again with less/smaller files.", "error");
                setUploading(false);
                return
            } else if (err.response && err.response.data && typeof err.response.data == "string") {
                if (err.response.data.startsWith("UERROR")) {
                    console.log("User error occurred when uploading files; response: ", err.response.data);
                    showToast("Something went wrong", err.response.data.substring("UERROR: ".length), "error");
                    setUploading(false);
                    return
                } else {
                    console.log("Unknown response from server when uploading files; response: ", err.response.data);
                }
            } else if (err.message && typeof err.message == "string") {
                console.log("Error occurred when uploading files; message: ", err.message);
            } else {
                console.log("Unknown error occurred when uploading files; error: ", err);
            }
            showToast("Something went wrong", "Couldn't upload files. Please try again.", "error");
            setUploading(false);
        }
    }

    const handleClose = () => {
        setFiles([]);
        setFileUploadResults({});
        setUploading(false);
        onClose();
    }

    const uploadButtonDisabled = files.length === 0 || uploading;

    return (
        <Modal onClose={handleClose} isOpen={isOpen} isCentered blockScrollOnMount closeOnOverlayClick={false} size={'md'}>
            <ModalOverlay />
            <ModalContent>
                <ModalHeader>Upload Files</ModalHeader>
                <ModalCloseButton />
                <ModalBody>
                    <Text>Files where the name is the same as an existing file in your directory will overwrite the existing file. New files are uploaded as normal. Filenames may be slightly modified for security purposes.</Text>
                    <FormControl mt={5} mb={5} isRequired>
                        <FormLabel><Text>Select one or more files.</Text></FormLabel>
                        <Input
                            key={"filesInput"}
                            type="file"
                            size="sm"
                            onChange={handleFileChange}
                            multiple
                        />
                        <Box mt={2}>
                            {files.length > 0 && (
                                <>
                                    <FormLabel>Selected files:</FormLabel>
                                    {files.map((file, index) => (
                                        <UploadFileCard key={index} index={index} fileName={file.name} uploading={uploading} uploadResults={fileUploadResults} handleRemoveFile={handleRemoveFile} />
                                    ))}
                                </>
                            )}
                        </Box>
                    </FormControl>
                </ModalBody>
                <ModalFooter>
                    <HStack spacing={"10px"}>
                        <Button variant="outline" onClick={handleClose}>Close</Button>
                        <Button variant={!uploading && !uploadButtonDisabled ? 'Default' : 'solid'} onClick={handleUpload} isLoading={uploading} loadingText="Uploading..." isDisabled={uploadButtonDisabled}>Upload</Button>
                    </HStack>
                </ModalFooter>
            </ModalContent>
        </Modal>
    )
}

export default UploadFilesModal