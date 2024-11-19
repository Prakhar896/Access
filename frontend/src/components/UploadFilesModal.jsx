import { Box, Button, Card, FormControl, FormLabel, Input, Modal, ModalBody, ModalCloseButton, ModalContent, ModalFooter, ModalHeader, ModalOverlay, Text, useDisclosure } from '@chakra-ui/react'
import React, { useState } from 'react'
import UploadFileCard from './UploadFileCard';

function UploadFilesModal({ isOpen, onClose, onOpen }) {
    const [files, setFiles] = useState([]);

    const handleFileChange = (event) => {
        const files = Array.from(event.target.files);
        setFiles((prevFiles) => [...prevFiles, ...files]);
    };

    const handleRemoveFile = (index) => {
        setFiles((prevFiles) => prevFiles.filter((_, fileIndex) => fileIndex !== index));
    };

    return (
        <Modal onClose={onClose} isOpen={isOpen} isCentered>
            <ModalOverlay />
            <ModalContent>
                <ModalHeader>Upload Files</ModalHeader>
                <ModalCloseButton />
                <ModalBody>
                    <FormControl mb={5} isRequired>
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
                                            <UploadFileCard key={index} index={index} imageName={file.name} handleRemoveFile={handleRemoveFile} />
                                        ))}
                                    </>
                                )}
                            </Box>
                        </FormControl>
                </ModalBody>
                <ModalFooter>
                    <Button onClick={onClose}>Close</Button>
                    <Button variant={'Default'}>Upload</Button>
                </ModalFooter>
            </ModalContent>
        </Modal>
    )
}

export default UploadFilesModal