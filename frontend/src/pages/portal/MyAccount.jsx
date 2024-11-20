import { useEffect, useState } from 'react'
import { Alert, AlertIcon, Box, Button, FormControl, FormLabel, Heading, Input, Modal, ModalBody, ModalCloseButton, ModalContent, ModalFooter, ModalHeader, ModalOverlay, Spacer, Spinner, Text, useDisclosure, useMediaQuery, useToast, VStack } from '@chakra-ui/react';
import configureShowToast from '../../components/showToast';
import { useSelector } from 'react-redux';
import server from '../../networking';
import { FaCheck, FaEllipsisH, FaSave } from 'react-icons/fa';

function MyAccount() {
    const { loaded } = useSelector(state => state.auth);
    const [limitedScreen] = useMediaQuery("(max-width: 800px)");
    const { isOpen: isChangePasswordModalOpen, onOpen: onChangePasswordModalOpen, onClose: onChangePasswordModalClose } = useDisclosure();

    const [profileData, setProfileData] = useState({});
    const [retrievingProfile, setRetrievingProfile] = useState(true);
    const [saveDisabled, setSaveDisabled] = useState(true);
    const [changePasswordDisabled, setChangePasswordDisabled] = useState(true);
    const [saving, setSaving] = useState(false);
    const [showingSaveSuccess, setShowingSaveSuccess] = useState(false);

    const [profileUsername, setProfileUsername] = useState("");
    const [profileEmail, setProfileEmail] = useState("");
    const [currentPassword, setCurrentPassword] = useState("");
    const [newPassword, setNewPassword] = useState("");

    const handleUsernameInputChange = (e) => { setProfileUsername(e.target.value); }
    const handleEmailInputChange = (e) => { setProfileEmail(e.target.value); }
    const handleCurrentPasswordInputChange = (e) => { setCurrentPassword(e.target.value); }
    const handleNewPasswordInputChange = (e) => { setNewPassword(e.target.value); }
    const handleChangePasswordModalClose = () => {
        setCurrentPassword("");
        setNewPassword("");
        onChangePasswordModalClose();
    }
    const handlePasswordUpdateProfile = () => {
        updateProfile(handleChangePasswordModalClose);
    }

    const toast = useToast();
    const showToast = configureShowToast(toast);

    const lastLoginDate = profileData.lastLogin ? new Date(profileData.lastLogin) : null;
    const creationDate = profileData.createdAt ? new Date(profileData.createdAt) : null;

    const getProfile = () => {
        server.post("/profile")
            .then(res => {
                if (res.status == 200 && typeof res.data == "object" && !Array.isArray(res.data)) {
                    setProfileData(res.data);
                    setRetrievingProfile(false);

                    if (res.data.username) {
                        setProfileUsername(res.data.username);
                    }
                    if (res.data.email) {
                        setProfileEmail(res.data.email);
                    }
                    return
                } else {
                    console.log("Non-200/unexpectedd response when retrieving profile; response: ", res.data);
                    showToast("Something went wrong", "Couldn't retrieve profile. Please try again.", "error");
                }
            })
            .catch(err => {
                if (err.response && err.response.data && typeof err.response.data == "string") {
                    if (err.response.data.startsWith("UERROR")) {
                        console.log("User error occurred in retrieving profile; response: ", err.response.data);
                        showToast("Something went wrong", err.response.data.substring("UERROR: ".length), "error");
                        return
                    } else {
                        console.log("Error occurred in retrieving profile; response: ", err.response.data);
                    }
                } else if (err.message && typeof err.message == "string") {
                    console.log("Error occurred in retrieving profile; message: ", err.message);
                } else {
                    console.log("Unknown error occurred in retrieving profile; error: ", err);
                }

                showToast("Something went wrong", "Couldn't retrieve profile. Please try again.", "error");
            })
    }


    const updateProfile = (handler=null) => {
        if (profileData.username == profileUsername && profileData.email == profileEmail && !currentPassword && !newPassword) {
            showToast("No changes detected", "You haven't made any changes to your profile.", "warning");
            return
        }

        var data = {};
        if (profileData.username != profileUsername) {
            data.username = profileUsername;
        }
        if (profileData.email != profileEmail) {
            data.email = profileEmail;
        }
        if (currentPassword && newPassword) {
            data.currentPassword = currentPassword;
            data.newPassword = newPassword;
        }

        setSaving(true);
        server.post('/profile/update', data)
            .then(res => {
                if (res.status == 200) {
                    if (typeof res.data == "string" && res.data.startsWith("SUCCESS")) {
                        showToast("Profile updated.", "", "success");
                        getProfile();
                        setSaveDisabled(true);
                        setShowingSaveSuccess(true);
                        setTimeout(() => {
                            setSaving(false);
                            setShowingSaveSuccess(false);
                        }, 2000);
                        if (handler) {
                            handler();
                        }
                        return
                    } else {
                        console.log("Unexpected response when updating profile; response:", res.data);
                    }
                } else {
                    console.log("Non-200 response when updating profile; response:", res.data);
                }

                showToast("Something went wrong", "Couldn't update profile. Please try again.", "error");
                setSaving(false);
            })
            .catch(err => {
                if (err.response && err.response.data && typeof err.response.data == "string") {
                    if (err.response.data.startsWith("UERROR")) {
                        console.log("User error occurred in updating profile; response: ", err.response.data);
                        showToast("Something went wrong", err.response.data.substring("UERROR: ".length), "error");
                        setSaving(false);
                        return
                    } else {
                        console.log("Error occurred in updating profile; response: ", err.response.data);
                    }
                } else if (err.message && typeof err.message == "string") {
                    console.log("Error occurred in updating profile; message: ", err.message);
                } else {
                    console.log("Unknown error occurred in updating profile; error: ", err);
                }

                showToast("Something went wrong", "Couldn't update profile. Please try again.", "error");
                setSaving(false);
            })
    }

    useEffect(() => {
        if (loaded) {
            getProfile();
        }
    }, [])

    useEffect(() => {
        if (profileData && !retrievingProfile) {
            if (profileUsername == profileData.username && profileEmail == profileData.email) {
                setSaveDisabled(true);
            } else {
                setSaveDisabled(false);
            }
        }
    }, [profileUsername, profileEmail])

    useEffect(() => {
        if (currentPassword && newPassword) {
            setChangePasswordDisabled(false);
        } else {
            setChangePasswordDisabled(true);
        }
    }, [currentPassword, newPassword])

    return (
        <>
            <Box display={'flex'} flexDir={'column'} justifyContent={'left'} m={!limitedScreen ? '1rem' : '10px'} p={'10px'}>
                <Box display={'flex'} justifyContent={'left'} flexDirection={'row'} alignItems={'center'}>
                    <Heading as={'h1'} fontSize={'3xl'} fontFamily={'Ubuntu'}>My Account</Heading>
                    <Spacer />
                    <Button variant={'Default'} onClick={onChangePasswordModalOpen}>
                        <FaEllipsisH />
                        {!limitedScreen && <Text ml={2}>Manage Password</Text>}
                    </Button>
                    <Button colorScheme='green' variant={'solid'} ml={"10px"} onClick={updateProfile} isDisabled={saveDisabled} isLoading={saving && !showingSaveSuccess}>{showingSaveSuccess ? <FaCheck /> : <FaSave />}</Button>
                </Box>

                <Box display={'flex'} justifyContent={'left'} flexDirection={'column'} alignItems={'left'} w={!limitedScreen ? '50%' : '100%'} mt={"5%"}>
                    {retrievingProfile ? (
                        <Spinner />
                    ) : (
                        <VStack spacing={"20px"}>
                            <FormControl>
                                <FormLabel><Text fontSize={'lg'}>Username</Text></FormLabel>
                                <Input value={profileUsername} onChange={handleUsernameInputChange} />
                            </FormControl>
                            <FormControl>
                                <FormLabel><Text fontSize={'lg'}>Email</Text></FormLabel>
                                <Input type='email' value={profileEmail} onChange={handleEmailInputChange} />
                            </FormControl>
                            {profileData.emailVerified == false && (
                                <Alert status='warning' rounded={'xl'}>
                                    <AlertIcon />
                                    <Text fontSize={{ base: 'sm', md: 'md' }}>Verify your email to use many of Access' features.</Text>
                                    <Spacer />
                                    <Button colorScheme='yellow' variant={'outline'} fontSize={{ base: 'sm', md: 'md' }} p={'14px'}>Resend Code</Button>
                                </Alert>
                            )}
                            <FormControl>
                                <FormLabel><Text fontSize={'lg'}>Last login</Text></FormLabel>
                                <Text>{lastLoginDate?.toLocaleString('en-GB', { dateStyle: "long", timeStyle: "short", hour12: true }) || "Unavailable"}</Text>
                            </FormControl>
                            <FormControl>
                                <FormLabel><Text fontSize={'lg'}>Created on</Text></FormLabel>
                                <Text>{creationDate?.toLocaleString('en-GB', { dateStyle: "long", timeStyle: "short", hour12: true }) || "Unavailable"}</Text>
                            </FormControl>
                        </VStack>
                    )}
                </Box>
            </Box>
            <Modal closeOnOverlayClick={false} isOpen={isChangePasswordModalOpen} onClose={handleChangePasswordModalClose} isCentered>
                <ModalOverlay />
                <ModalContent>
                    <ModalHeader>Change password</ModalHeader>
                    <ModalCloseButton />
                    <ModalBody>
                        <VStack spacing={"10px"} alignItems={"flex-start"}>
                            <Text>Please note that this action is irreversible. For security, you need to provide your current password.</Text>
                            <FormControl>
                                <FormLabel>Current password</FormLabel>
                                <Input type='password' value={currentPassword} onChange={handleCurrentPasswordInputChange} />
                            </FormControl>
                            <FormControl>
                                <FormLabel>New password</FormLabel>
                                <Input type='password' value={newPassword} onChange={handleNewPasswordInputChange} />
                            </FormControl>
                        </VStack>
                    </ModalBody>

                    <ModalFooter>
                        <Button variant={'outline'} onClick={handleChangePasswordModalClose}>Cancel</Button>
                        <Button variant={!saving && !changePasswordDisabled ? 'Default': 'solid'} ml={"10px"} onClick={handlePasswordUpdateProfile} isDisabled={changePasswordDisabled} isLoading={saving} loadingText={"Changing..."}>Change</Button>
                    </ModalFooter>
                </ModalContent>
            </Modal>
        </>
    )
}

export default MyAccount;