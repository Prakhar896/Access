import { useEffect, useState } from 'react'
import { Alert, AlertIcon, Box, Button, FormControl, FormLabel, Heading, Input, Modal, ModalBody, ModalCloseButton, ModalContent, ModalFooter, ModalHeader, ModalOverlay, Spacer, Spinner, Text, useDisclosure, useMediaQuery, useToast, VStack } from '@chakra-ui/react';
import configureShowToast from '../../components/showToast';
import { useSelector } from 'react-redux';
import server from '../../networking';
import { FaCheck, FaEllipsisH, FaSave } from 'react-icons/fa';
import AuditLogsList from '../../components/AuditLogsList';
import DeleteAccountButton from '../../components/DeleteAccountButton';
import { useNavigate } from 'react-router-dom';

function MyAccount() {
    const { accountID, loaded } = useSelector(state => state.auth);
    const navigate = useNavigate();
    const [limitedScreen] = useMediaQuery("(max-width: 800px)");
    const { isOpen: isChangePasswordModalOpen, onOpen: onChangePasswordModalOpen, onClose: onChangePasswordModalClose } = useDisclosure();

    const [profileData, setProfileData] = useState({});
    const [retrievingProfile, setRetrievingProfile] = useState(true);
    const [auditLogsData, setAuditLogsData] = useState([]);
    const [retrievingAuditLogs, setRetrievingAuditLogs] = useState(false);
    const [resendingVerificationEmail, setResendingVerificationEmail] = useState(false);
    const [resendSuccess, setResendSuccess] = useState(false);
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


    const updateProfile = (handler = null) => {
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
                        if (handler && typeof handler == "function") {
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

    const processAuditLogs = (data) => {
        var logs = [];

        for (var log of data) {
            log["originalTimestamp"] = structuredClone(log["timestamp"]);
            log["timestamp"] = new Date(log["timestamp"]).toLocaleString('en-GB', { dateStyle: "long", timeStyle: "medium", hour12: true });
            logs.push(log);
        }

        logs.sort((a, b) => {
            // Sort by timestamp in descending order
            return new Date(b["originalTimestamp"]) - new Date(a["originalTimestamp"]);
        })

        return logs;
    }

    const retrieveAuditLogs = async () => {
        setRetrievingAuditLogs(true);
        server.post("/profile/auditLogs")
            .then(res => {
                if (res.status == 200) {
                    if (typeof res.data == "object" && !Array.isArray(res.data)) {
                        setAuditLogsData(processAuditLogs(Object.values(res.data)));
                        setRetrievingAuditLogs(false);
                        return;
                    } else {
                        console.log("Unexpected response in retrieving audit logs; response:", res.data);
                    }
                } else {
                    console.log("Non-200 status code in retrieving audit logs; response:", res.data);
                }

                showToast("Something went wrong", "Couldn't retrieve audit logs. Please try again later.", "error");
                setRetrievingAuditLogs(false);
            })
            .catch(err => {
                if (err.response && err.response.data && typeof err.response.data == "string") {
                    if (err.response.data.startsWith("UERROR")) {
                        console.log("User error occurred in retrieving audit logs; response:", err.response.data);
                        showToast("Something went wrong", err.response.data.substring("UERROR: ".length), "error");
                        setRetrievingAuditLogs(false);
                        return;
                    } else {
                        console.log("Error occurred in retrieving audit logs; response:", err.response.data);
                    }
                } else if (err.message && typeof err.message == "string") {
                    console.log("Error occurred in retrieving audit logs; message:", err.message);
                } else {
                    console.log("Unknown error occurred in retrieving audit logs; error:", err);
                }

                showToast("Something went wrong", "Couldn't retrieve audit logs. Please try again later.", "error");
                setRetrievingAuditLogs(false);
            })
    }

    const resendVerificationEmail = async () => {
        setResendingVerificationEmail(true);
        server.post("/identity/resendEmailVerification")
        .then(res => {
            if (res.status == 200) {
                if (typeof res.data == "string" && res.data.startsWith("SUCCESS")) {
                    showToast("Verification email sent.", res.data.substring("SUCCESS: ".length), "success");
                    setResendingVerificationEmail(false);
                    setResendSuccess(true);
                    return
                } else {
                    console.log("Unexpected response in resending verification email; response:", res.data);
                }
            } else {
                console.log("Non-200 status code in resending verification email; response:", res.data);
            }

            showToast("Something went wrong", "Couldn't resend verification email. Please try again.", "error");
            setResendingVerificationEmail(false);
        })
        .catch(err => {
            if (err.response && err.response.data && typeof err.response.data == "string") {
                if (err.response.data.startsWith("UERROR")) {
                    console.log("User error occurred in resending verification email; response:", err.response.data);
                    showToast("Something went wrong", err.response.data.substring("UERROR: ".length), "error");
                    setResendingVerificationEmail(false);
                    return;
                } else {
                    console.log("Error occurred in resending verification email; response:", err.response.data);
                }
            } else if (err.message && typeof err.message == "string") {
                console.log("Error occurred in resending verification email; message:", err.message);
            } else {
                console.log("Unknown error occurred in resending verification email; error:", err);
            }

            showToast("Something went wrong", "Couldn't resend verification email. Please try again.", "error");
            setResendingVerificationEmail(false);
        })
    }

    const handleResendClick = () => {
        if (!resendSuccess) {
            resendVerificationEmail();
        } else {
            if (accountID) {
                navigate('/verifyEmail?id=' + accountID);
            } else {
                showToast("Something went wrong", "Couldn't redirect to verification page. Please try again.", "error");
            }
        }
    }

    useEffect(() => {
        if (loaded) {
            getProfile();
            retrieveAuditLogs();
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

                <Box display={'flex'} justifyContent={'left'} flexDirection={'row'} alignItems={'flex-start'}>
                    <Box display={'flex'} justifyContent={'left'} flexDirection={'column'} alignItems={'left'} w={!limitedScreen ? '50%' : '100%'} mt={"5%"}>
                        {retrievingProfile ? (
                            <Spinner />
                        ) : (
                            <>
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
                                            <Button colorScheme='yellow' variant={'outline'} fontSize={{ base: 'xs', sm: 'sm', md: 'md' }} p={'14px'} onClick={handleResendClick} isLoading={resendingVerificationEmail} loadingText="Resending..." isDisabled={resendingVerificationEmail}>{resendSuccess ? "Input Code": "Resend Code"}</Button>
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
                                {limitedScreen && <AuditLogsList auditLogsData={auditLogsData} retrievingAuditLogs={retrievingAuditLogs} />}

                                <DeleteAccountButton />
                            </>
                        )}
                    </Box>

                    {!limitedScreen && (
                        <Box display={'flex'} justifyContent={'left'} flexDirection={'column'} alignItems={'left'} w={'50%'} mt={"5%"}>
                            <AuditLogsList auditLogsData={auditLogsData} retrievingAuditLogs={retrievingAuditLogs} />
                        </Box>
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
                        <Button variant={!saving && !changePasswordDisabled ? 'Default' : 'solid'} ml={"10px"} onClick={handlePasswordUpdateProfile} isDisabled={changePasswordDisabled} isLoading={saving} loadingText={"Changing..."}>Change</Button>
                    </ModalFooter>
                </ModalContent>
            </Modal>
        </>
    )
}

export default MyAccount;