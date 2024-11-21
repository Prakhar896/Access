import { Box, Button, FormControl, FormLabel, Heading, Image, Input, ScaleFade, Spacer, Text, useMediaQuery, useToast, VStack } from '@chakra-ui/react'
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import configureShowToast from '../components/showToast';
import colouredLogo from '/logo/svg/logo-color.svg';
import server from '../networking';

function ForgotPassword() {
    const [limitedScreen] = useMediaQuery("(max-width: 800px)")
    const navigate = useNavigate();
    const toast = useToast();
    const showToast = configureShowToast(toast);

    const [usernameOrEmail, setUsernameOrEmail] = useState('')
    const [showingPasswordSection, setShowingPasswordSection] = useState(false)
    const [resetKey, setResetKey] = useState('')
    const [newPassword, setNewPassword] = useState('')
    const [confirmPassword, setConfirmPassword] = useState('')
    const [resetLoading, setResetLoading] = useState(false)

    const handleUsernameOrEmailChange = (e) => { setUsernameOrEmail(e.target.value) }
    const handleResetKeyChange = (e) => { setResetKey(e.target.value) }
    const handleNewPasswordChange = (e) => { setNewPassword(e.target.value) }
    const handleConfirmPasswordChange = (e) => { setConfirmPassword(e.target.value) }
    const handleEnter = (e) => { if (e.key === 'Enter') { resetPassword() } }

    const buttonDisabled = !usernameOrEmail || (showingPasswordSection && (!resetKey || !newPassword || !confirmPassword))

    const resetPassword = () => {
        if (!usernameOrEmail) {
            showToast('Please fill in all fields', '', 'error')
            return
        }

        if (showingPasswordSection) {
            if (!resetKey || !newPassword || !confirmPassword) {
                showToast('Please fill in all fields', '', 'error')
                return
            }
            if (newPassword !== confirmPassword) {
                showToast('Passwords do not match', '', 'error')
                return
            }
        }

        var data = {
            usernameOrEmail: usernameOrEmail
        };
        if (showingPasswordSection) {
            data["reset"] = {
                key: resetKey,
                newPassword: newPassword
            }
        }

        setResetLoading(true)
        server.post("/identity/forgotPassword", data)
        .then(res => {
            if (res.status == 200) {
                if (typeof res.data == "string" && res.data.startsWith("SUCCESS")) {
                    if (!showingPasswordSection) {
                        showToast("Success", "If this account exists, an email with a reset key was dispatched. Retrieve to continue.", "success")
                        setResetLoading(false);
                        setShowingPasswordSection(true)
                        return;
                    } else {
                        showToast("Success", "Password reset successfully!", "success")
                        navigate('/login')
                        return;
                    }
                } else {
                    console.log("Unexpected response in resetting password; response:", res.data);
                }
            } else {
                console.log("Non-200 status code in resetting password; response:", res.data);
            }

            showToast("Something went wrong", "An error occurred. Please try again.", "error")
            setResetLoading(false)
        })
        .catch(err => {
            if (err.response && err.response.data && typeof err.response.data == "string") {
                if (err.response.data.startsWith("UERROR")) {
                    console.log("User error occurred in resetting password; response:", err.response.data);
                    showToast("Something went wrong", err.response.data.substring("UERROR: ".length), "error")
                    setResetLoading(false);
                    return;
                } else {
                    console.log("Error occurred in resetting password; response:", err.response.data);
                }
            } else if (err.message && typeof err.message == "string") {
                console.log("Error occurred in resetting password; error:", err.message);
            } else {
                console.log("Unknown error occurred in resetting password; error:", err);
            }

            showToast("Something went wrong", "An error occurred. Please try again.", "error")
            setResetLoading(false)
        })
    }

    return (
        <Box display={'flex'} flexDirection={'column'} justifyContent={'center'} maxW={'100%'} p={!limitedScreen ? '10px' : '0px'}>
            <Box display={'flex'} flexDirection={'column'} justifyContent={'space-between'} alignItems={'center'} mt={'10%'} mb={"20px"}>
                <Spacer />
                <Link to={'/'}>
                    <Image src={colouredLogo} alt={'Logo'} maxH={'100px'} rounded={'xl'} />
                </Link>
                <Spacer />
                <Box display={'flex'} flexDir={'column'} justifyContent={'left'} alignItems={'center'} maxW={limitedScreen ? '70%' : '50%'} p={!limitedScreen ? '10px' : '0px'} mt={limitedScreen ? '20px' : '0px'}>
                    <ScaleFade in={true} initialScale={0.9}>
                        <Box display={'flex'} flexDir={'column'} alignItems={'center'}>
                            <Heading as={'h1'} size={'xl'}>Forgot Password</Heading>
                            <Text mt={"15px"}>Need to reset your password?</Text>
                            <Text>No worries, issue a reset key and change your password!</Text>
                            <VStack spacing={4} mt={10}>
                                <FormControl id='username' required>
                                    <FormLabel>Username or Email</FormLabel>
                                    <Input onKeyUp={handleEnter} placeholder='e.g johndoe/johndoe@email.com' type='text' w={{ base: 'xs', md: 'md', lg: 'lg' }} id='usernameOrEmailInput' value={usernameOrEmail} onChange={handleUsernameOrEmailChange} isDisabled={showingPasswordSection} required />
                                </FormControl>
                                {showingPasswordSection && (
                                    <>
                                        <FormControl id='resetKeyInput' required>
                                            <FormLabel>Reset Key (from email inbox)</FormLabel>
                                            <Input onKeyUp={handleEnter} placeholder='Check your inbox' type='text' value={resetKey} onChange={handleResetKeyChange} required />
                                        </FormControl>
                                        <FormControl id='newPasswordInput' required>
                                            <FormLabel>New Password</FormLabel>
                                            <Input onKeyUp={handleEnter} placeholder='Uppercase and numeric letters required' type='password' value={newPassword} onChange={handleNewPasswordChange} required />
                                        </FormControl>
                                        <FormControl id='confirmPasswordInput' required>
                                            <FormLabel>Confirm Password</FormLabel>
                                            <Input onKeyUp={handleEnter} placeholder='Re-enter the same password' type='password' value={confirmPassword} onChange={handleConfirmPasswordChange} required />
                                        </FormControl>
                                    </>
                                )}
                            </VStack>
                            <VStack mt={'10%'}>
                                {!showingPasswordSection && <Text>Know your password? <Button variant={'link'} color={'black'} onClick={() => navigate('/login')} >Login here.</Button></Text>}
                                <Button variant={!resetLoading && !buttonDisabled ? 'Default' : 'solid'} w={{ base: 'xs', md: 'md', lg: 'lg' }} onClick={resetPassword} isLoading={resetLoading} isDisabled={buttonDisabled}>{showingPasswordSection ? "Reset": "Send Reset Key"}</Button>
                            </VStack>
                        </Box>
                    </ScaleFade>
                </Box>
                <Spacer />
            </Box>
        </Box>
    )
}

export default ForgotPassword