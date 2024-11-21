import { Button, Divider, FormControl, FormLabel, Input, MenuItem, Modal, ModalBody, ModalCloseButton, ModalContent, ModalFooter, ModalHeader, ModalOverlay, Spinner, Text, useDisclosure, useToast, VStack, Link as ChakraLink, useClipboard } from '@chakra-ui/react'
import React, { useEffect, useState } from 'react'
import { BsFillShareFill } from 'react-icons/bs'
import server from '../../networking';
import configureShowToast from '../showToast';
import { Link } from 'react-router-dom';

function ShareFile({ fileData }) {
    const { isOpen: isShareModalOpen, onOpen: onShareModalOpen, onClose: onShareModalClose } = useDisclosure();
    const [sharingInfo, setSharingInfo] = useState({});
    const { onCopy, value, setValue, hasCopied } = useClipboard('')

    const [gettingSharingInfo, setGettingSharingInfo] = useState(true);
    const [startingSharing, setStartingSharing] = useState(false);
    const [togglingSharing, setTogglingSharing] = useState(false);
    const [revokingSharing, setRevokingSharing] = useState(false);

    const [sharePassword, setSharePassword] = useState("");

    const handleSharePasswordChange = (e) => { setSharePassword(e.target.value); }

    const toast = useToast();
    const showToast = configureShowToast(toast);

    const getSharingInfo = async () => {
        setGettingSharingInfo(true);
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
        if (!sharingInfo.linkCode) {
            showToast("Sharing not active.", "", "info");
            return
        }
        if (sharingInfo.active == undefined || sharingInfo.active == null || typeof sharingInfo.active != "boolean") {
            showToast("Sharing status unknown.", "", "info");
            return
        }

        const newStatus = !sharingInfo.active;
        setTogglingSharing(true);
        server.post("/sharing/toggleActiveStatus", {
            fileID: fileData.id,
            newStatus: newStatus
        })
            .then(res => {
                if (res.status == 200) {
                    if (typeof res.data == "string" && res.data.startsWith("SUCCESS")) {
                        setTogglingSharing(false);
                        getSharingInfo();
                        return;
                    } else {
                        console.log(`Unexpected response in toggling sharing for file ${fileData.id}; response:`, res.data);
                    }
                } else {
                    console.log(`Non-200 status code in toggling sharing for file ${fileData.id}; response:`, res.data);
                }

                showToast("Something went wrong", "Couldn't toggle sharing status. Please try again.", "error");
                setTogglingSharing(false);
            })
            .catch(err => {
                if (err.response && err.response.data && typeof err.response.data == "string") {
                    if (err.response.data.startsWith("UERROR")) {
                        console.log(`User error occurred in toggling sharing for file ${fileData.id}; response:`, err.response.data);
                        showToast("Something went wrong", err.response.data.substring("UERROR: ".length), "error");
                        setTogglingSharing(false);
                        return;
                    } else {
                        console.log(`Error occurred in toggling sharing for file ${fileData.id}; response:`, err.response.data);
                    }
                } else if (err.message && typeof err.message == "string") {
                    console.log(`Error occurred in toggling sharing for file ${fileData.id}; error:`, err.message);
                } else {
                    console.log(`Unknown error occurred in toggling sharing for file ${fileData.id}; error:`, err);
                }

                showToast("Something went wrong", "Couldn't toggle sharing status. Please try again.", "error");
                setTogglingSharing(false);
            })
    }

    const revokeSharing = async () => {
        if (!sharingInfo.linkCode) {
            showToast("Sharing not active.", "", "info");
            return
        }

        setRevokingSharing(true);
        server.post("/sharing/revoke", {
            fileID: fileData.id
        })
            .then(res => {
                if (res.status == 200) {
                    if (typeof res.data == "string" && res.data.startsWith("SUCCESS")) {
                        setRevokingSharing(false);
                        getSharingInfo();
                        return;
                    } else {
                        console.log(`Unexpected response in revoking sharing for file ${fileData.id}; response:`, res.data);
                    }
                } else {
                    console.log(`Non-200 status code in revoking sharing for file ${fileData.id}; response:`, res.data);
                }

                showToast("Something went wrong", "Couldn't revoke sharing. Please try again.", "error");
                setRevokingSharing(false);
            })
            .catch(err => {
                if (err.response && err.response.data && typeof err.response.data == "string") {
                    if (err.response.data.startsWith("UERROR")) {
                        console.log(`User error occurred in revoking sharing for file ${fileData.id}; response:`, err.response.data);
                        showToast("Something went wrong", err.response.data.substring("UERROR: ".length), "error");
                        setRevokingSharing(false);
                        return;
                    } else {
                        console.log(`Error occurred in revoking sharing for file ${fileData.id}; response:`, err.response.data);
                    }
                } else if (err.message && typeof err.message == "string") {
                    console.log(`Error occurred in revoking sharing for file ${fileData.id}; error:`, err.message);
                } else {
                    console.log(`Unknown error occurred in revoking sharing for file ${fileData.id}; error:`, err);
                }

                showToast("Something went wrong", "Couldn't revoke sharing. Please try again.", "error");
                setRevokingSharing(false);
            })
    }

    useEffect(() => {
        if (isShareModalOpen && fileData.id) {
            getSharingInfo();
        }
    }, [isShareModalOpen, fileData])

    useEffect(() => {
        if (sharingInfo.linkCode) {
            setValue(`${window.location.origin}/s?code=${sharingInfo.linkCode}`);
        }
    }, [sharingInfo])

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
                            <VStack alignItems={"flex-start"} w={"100%"} spacing={"10px"}>
                                <Text>Sharing Active</Text>
                                <Text fontWeight={'bold'} color={sharingInfo.linkCode && sharingInfo.active ? "green" : "red"}>{sharingInfo.linkCode && sharingInfo.active ? "Yes" : "No"}{sharingInfo.linkCode ? ` (${sharingInfo.linkCode})` : ""}</Text>
                                {sharingInfo.linkCode ? (
                                    <>
                                        <Text>Share Link</Text>
                                        <Button variant={'Default'} onClick={onCopy}>{hasCopied ? "Copied!" : "Copy Share Link"}</Button>
                                        <Text>Password Required</Text>
                                        <Text fontWeight={'bold'}>{sharingInfo.passwordRequired ? "Yes" : "No"}</Text>
                                        <Text>File name</Text>
                                        <Text fontWeight={'bold'}>{sharingInfo.name}</Text>
                                        <Text>Downloads</Text>
                                        <Text fontWeight={'bold'}>{sharingInfo.accessors}</Text>
                                    </>
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
                            </VStack>
                        )}
                    </ModalBody>
                    <ModalFooter>
                        <Button variant={'outline'} onClick={onShareModalClose}>Close</Button>
                        {sharingInfo.linkCode ? (
                            <>
                                <Button variant={'outline'} colorScheme={sharingInfo.active ? 'red' : 'green'} ml={"10px"} onClick={toggleSharing} isDisabled={gettingSharingInfo || togglingSharing || revokingSharing} isLoading={togglingSharing} loadingText={sharingInfo.active ? "Deactivating..." : "Activating..."}>{sharingInfo.active ? "Deactivate" : "Activate"}</Button>
                                <Button variant={'solid'} colorScheme='red' ml={"10px"} onClick={revokeSharing} isDisabled={gettingSharingInfo || togglingSharing || revokingSharing} isLoading={revokingSharing} loadingText={"Stopping..."}>Stop Sharing</Button>
                            </>
                        ) : (
                            <Button variant={!startingSharing ? 'Default' : 'solid'} ml={"10px"} onClick={startSharing} isDisabled={gettingSharingInfo || togglingSharing || revokingSharing} isLoading={startingSharing} loadingText={"Starting..."}>Start Sharing</Button>
                        )}
                    </ModalFooter>
                </ModalContent>
            </Modal>
        </>
    )
}

export default ShareFile