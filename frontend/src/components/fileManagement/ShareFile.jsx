import { Button, Divider, FormControl, FormLabel, Input, MenuItem, Modal, ModalBody, ModalCloseButton, ModalContent, ModalFooter, ModalHeader, ModalOverlay, Spinner, Text, useDisclosure, useToast } from '@chakra-ui/react'
import React, { useEffect, useState } from 'react'
import { BsFillShareFill } from 'react-icons/bs'
import server from '../../networking';
import configureShowToast from '../showToast';

function ShareFile({ fileData }) {
    const { isOpen: isShareModalOpen, onOpen: onShareModalOpen, onClose: onShareModalClose } = useDisclosure();
    const [sharingInfo, setSharingInfo] = useState({});

    const [gettingSharingInfo, setGettingSharingInfo] = useState(true);
    const [startingSharing, setStartingSharing] = useState(false);
    const [togglingSharing, setTogglingSharing] = useState(false);
    const [revokingSharing, setRevokingSharing] = useState(false);

    const [sharePassword, setSharePassword] = useState("");

    const handleSharePasswordChange = (e) => { setSharePassword(e.target.value); }

    const toast = useToast();
    const showToast = configureShowToast(toast);

    const getSharingInfo = async () => {
        server.post("/sharing/info", {
            fileID: fileData.id
        })
            .then(res => {
                if (res.status == 200) {
                    if (typeof res.data == "object" && !Array.isArray(res.data)) {
                        setSharingInfo(res.data);
                        setGettingSharingInfo(false);
                        return;
                    } else {
                        console.log(`Unexpected response in retrieving sharing info for file ${fileData.id}; response:`, res.data);
                    }
                } else {
                    console.log(`Non-200 status code in getting sharing info for file ${fileData.id}; response:`, res.data);
                }

                showToast("Something went wrong", "Couldn't get sharing information. Please try again.", "error");
                setGettingSharingInfo(false);
            })
            .catch(err => {
                if (err.response && err.response.data && typeof err.response.data == "string") {
                    if (err.response.data.startsWith("UERROR")) {
                        console.log(`User error occurred in retrieving file sharing info for file ${fileData.id}; response:`, err.response.data);
                        showToast("Something went wrong", err.response.data.substring("UERROR: ".length), "error");
                        setGettingSharingInfo(false);
                        return;
                    } else {
                        console.log(`Error occurred in retrieving file sharing info for file ${fileData.id}; response:`, err.response.data);
                    }
                } else if (err.message && typeof err.message == "string") {
                    console.log(`Error occurred in retrieving file sharing info for file ${fileData.id}; error:`, err.message);
                } else {
                    console.log(`Unknown error occurred in retrieving file sharing info for file ${fileData.id}; error:`, err);
                }

                showToast("Something went wrong", "Couldn't get sharing information. Please try again.", "error");
                setGettingSharingInfo(false);
            })
    }

    const startSharing = async () => {
        if (sharingInfo.linkCode) {
            showToast("Sharing already active.", "", "info");
            return
        }

        var password = false;
        if (sharePassword) {
            password = sharePassword;
        }

        setStartingSharing(true);
        server.post("/sharing/new", {
            fileID: fileData.id,
            password: password
        })
            .then(res => {
                if (res.status == 200) {
                    if (typeof res.data == "object" && !Array.isArray(res.data)) {
                        if (res.data.message && typeof res.data.message == "string" && res.data.message.startsWith("SUCCESS")) {
                            setStartingSharing(false);
                            setSharePassword("");
                            getSharingInfo();
                            return;
                        } else {
                            console.log(`Unexpected response in starting sharing for file ${fileData.id}; response:`, res.data);
                        }
                    } else {
                        console.log(`Unexpected response in starting sharing for file ${fileData.id}; response:`, res.data);
                    }
                } else {
                    console.log(`Non-200 status code in starting sharing for file ${fileData.id}; response:`, res.data);
                }

                showToast("Something went wrong", "Couldn't start sharing. Please try again.", "error");
                setStartingSharing(false);
            })
            .catch(err => {
                if (err.response && err.response.data && typeof err.response.data == "string") {
                    if (err.response.data.startsWith("UERROR")) {
                        console.log(`User error occurred in starting sharing for file ${fileData.id}; response:`, err.response.data);
                        showToast("Something went wrong", err.response.data.substring("UERROR: ".length), "error");
                        setStartingSharing(false);
                        return;
                    } else {
                        console.log(`Error occurred in starting sharing for file ${fileData.id}; response:`, err.response.data);
                    }
                } else if (err.message && typeof err.message == "string") {
                    console.log(`Error occurred in starting sharing for file ${fileData.id}; error:`, err.message);
                } else {
                    console.log(`Unknown error occurred in starting sharing for file ${fileData.id}; error:`, err);
                }

                showToast("Something went wrong", "Couldn't start sharing. Please try again.", "error");
                setStartingSharing(false);
            })
    }

    const toggleSharing = async () => {

    }

    const revokeSharing = async () => {
    }

    useEffect(() => {
        if (isShareModalOpen && fileData.id) {
            getSharingInfo();
        }
    }, [isShareModalOpen])

    console.log(sharingInfo)

    return (
        <>
            <MenuItem icon={<BsFillShareFill />} onClick={onShareModalOpen}>
                Sharing...
            </MenuItem>
            <Modal size={'lg'} onClose={onShareModalClose} isOpen={isShareModalOpen} closeOnOverlayClick={false} isCentered>
                <ModalOverlay />
                <ModalContent>
                    <ModalHeader>Sharing</ModalHeader>
                    <ModalCloseButton />
                    <ModalBody>
                        {gettingSharingInfo ? (
                            <Spinner />
                        ) : (
                            <>
                                <Text>Sharing Active</Text>
                                <Text fontWeight={'bold'}>{sharingInfo.linkCode ? "Yes" : "No"}</Text>
                                {sharingInfo.linkCode ? (
                                    <Text>WIP</Text>
                                ) : (
                                    <>
                                        <Divider mt={"15px"} />
                                        <Text fontWeight={'bold'} fontSize={'lg'} mt={"20px"}>Start Sharing</Text>
                                        <Text>Create a public link that can be used by anyone to access this file. Optionally, password protect it.</Text>
                                        <FormControl mt={"15px"}>
                                            <FormLabel>Password (Optional)</FormLabel>
                                            <Input type='password' placeholder='Set a password for your file share' value={sharePassword} onChange={handleSharePasswordChange} isDisabled={startingSharing} />
                                        </FormControl>
                                    </>
                                )}
                            </>
                        )}
                    </ModalBody>
                    <ModalFooter>
                        <Button variant={'outline'} onClick={onShareModalClose}>Close</Button>
                        {sharingInfo.linkCode ? (
                            <>
                                <Button variant={'outline'} colorScheme={sharingInfo.active ? 'red' : 'green'} ml={"10px"} onClick={toggleSharing}>{sharingInfo.active ? "Deactivate" : "Activate"}</Button>
                                <Button variant={'solid'} colorScheme='red' ml={"10px"} onClick={revokeSharing}>Stop Sharing</Button>
                            </>
                        ) : (
                            <Button variant={!startingSharing ? 'Default': 'solid'} ml={"10px"} onClick={startSharing} isLoading={startingSharing} loadingText={"Starting..."}>Start Sharing</Button>
                        )}
                    </ModalFooter>
                </ModalContent>
            </Modal>
        </>
    )
}

export default ShareFile