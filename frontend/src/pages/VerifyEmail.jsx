import React, { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux';
import { Link, useLocation, useNavigate, useSearchParams } from 'react-router-dom'
import configureShowToast from '../components/showToast';
import { Box, Button, FormControl, FormLabel, Heading, Image, Input, ScaleFade, Spacer, Spinner, Text, useMediaQuery, useToast, VStack } from '@chakra-ui/react';
import CentredSpinner from '../components/CentredSpinner';
import colouredLogo from '/logo/svg/logo-color.svg';
import server from '../networking';

function VerifyEmail() {
    const navigate = useNavigate();
    const { state } = useLocation();
    const [searchParams] = useSearchParams();
    const [message, setMessage] = useState('Verifying...');
    const [messageColour, setMessageColour] = useState('black');
    const [messageHidden, setMessageHidden] = useState(true);
    const [codeInputHidden, setCodeInputHidden] = useState(true);
    const [codeLengthHitOnce, setCodeLengthHitOnce] = useState(false);
    const [verificationLoading, setVerificationLoading] = useState(false);
    const [limitedScreen] = useMediaQuery("(max-width: 800px)");
    const toast = useToast()
    const showToast = configureShowToast(toast);
    const { username, loaded } = useSelector(state => state.auth);
    const [code, setCode] = useState(searchParams.get('code') || '');
    const [userID, setUserID] = useState(searchParams.get('id') || '');
    const [email, setEmail] = useState('');
    const [fromCreateAccount, setFromCreateAccount] = useState(state && state.fromCreateAccount ? true : false);

    const buttonDisabled = !code || !userID;

    const handleCodeChange = (e) => {
        if (e.target.value.length === 6 && !codeLengthHitOnce) {
            setCodeLengthHitOnce(true);
        }
        setCode(e.target.value);
    };
    const handleFieldEnter = (e) => { if (e.key === 'Enter') { verifyOTP(); } }
    const updateMessageField = (message, status) => {
        setMessage(message);
        setMessageHidden(false);

        if (status === 'error') {
            setMessageColour('red');
        } else if (status === 'success') {
            setMessageColour('green');
        } else {
            setMessageColour('black');
        }
    }

    const verifyOTP = (id = structuredClone(userID)) => {
        if (!id) {
            updateMessageField('Invalid verification link.', 'error');
            return;
        }
        if (code.length !== 6) {
            updateMessageField('Invalid verification code.', 'error');
            setCodeInputHidden(false);
            return;
        }

        setVerificationLoading(true);
        setMessageHidden(true);
        server.post('/identity/verifyOTP', {
            userID: id,
            otpCode: code
        })
            .then(response => {
                if (response.status === 200) {
                    if (response.data && typeof response.data === 'string') {
                        if (response.data.startsWith('SUCCESS')) {
                            showToast('Email verified!', '', 'success');
                            if (fromCreateAccount) {
                                navigate('/login', {
                                    state: {
                                        email: email
                                    }
                                });
                            } else if (window.history.length > 1) {
                                navigate(-1);
                            } else {
                                navigate('/');
                            }
                        } else {
                            console.log("Unknown response from server in login; response:", response.data);
                            showToast('Something went wrong', "Couldn't verify email. Please try again.", 'error');
                        }
                    } else {
                        console.log("Unexpected response in login; response:", response.data);
                        showToast('Something went wrong', "Couldn't verify email. Please try again.", 'error');
                    }
                } else {
                    console.log("Non-200 status code in login; response:", response.data);
                    showToast('Something went wrong', "Couldn't verify email. Please try again.", 'error');
                }

                setVerificationLoading(false);
                setCodeInputHidden(false);
            })
            .catch(err => {
                if (err.response && err.response.data && typeof err.response.data == "string") {
                    if (err.response.data.startsWith("UERROR")) {
                        console.log("User error occurred in login; response:", err.response.data);
                        updateMessageField(err.response.data.substring("UERROR: ".length), 'error');
                    } else {
                        console.log("Error occurred in login; response:", err.response.data);
                        showToast('Something went wrong', "Couldn't verify email. Please try again.", 'error');
                    }
                } else if (err.message) {
                    console.log("Error occurred in login; message:", err.message);
                    showToast('Something went wrong', "Couldn't verify email. Please try again.", 'error');
                } else {
                    console.log("Unknown error occurred in login; error:", err);
                    showToast('Something went wrong', "Couldn't verify email. Please try again.", 'error');
                }

                setVerificationLoading(false);
                setCodeInputHidden(false);
            })
    }

    useEffect(() => {
        var id = structuredClone(userID);
        if (state) {
            if (state.userID) {
                setUserID(state.userID);
                id = state.userID;
            }
            if (state.email) {
                setEmail(state.email);
            }
        }

        if (!id) {
            showToast("Invalid verification link", 'Please try again.', 'error');
            navigate('/');
            return
        }
        if (!code) {
            setCodeInputHidden(false);
            return
        } else {
            verifyOTP(id);
        }
    }, [])

    useEffect(() => {
        if (codeLengthHitOnce) {
            verifyOTP();
        }
    }, [code])

    if (!loaded) {
        return <CentredSpinner />
    }

    return (
        <Box display={'flex'} flexDirection={'column'} justifyContent={'center'} maxW={'100%'} p={!limitedScreen ? '10px' : '0px'}>
            <Box display={'flex'} flexDirection={'column'} justifyContent={'space-between'} alignItems={'center'} mt={!limitedScreen ? '10%' : '20%'}>
                <Spacer />
                <Link to={'/'}>
                    <Image src={colouredLogo} alt={'Logo'} maxH={'100px'} rounded={'xl'} />
                </Link>
                <Spacer />
                <Box display={'flex'} flexDir={'column'} justifyContent={'left'} alignItems={'center'} maxW={limitedScreen ? '70%' : '50%'} p={!limitedScreen ? '10px' : '0px'} mt={limitedScreen ? '20px' : '0px'}>
                    <ScaleFade in={true} initialScale={0.9}>
                        <Box display={'flex'} flexDir={'column'} alignItems={'center'}>
                            <Heading as={'h1'} size={'xl'}>Verify your email</Heading>
                            <VStack spacing={4} mt={10} hidden={codeInputHidden}>
                                <FormControl id='username' required>
                                    <FormLabel>Verification Code</FormLabel>
                                    <Input onKeyUp={handleFieldEnter} placeholder='Check your inbox' type='text' w={{ base: 'xs', md: 'md', lg: 'lg' }} value={code} onChange={handleCodeChange} disabled={verificationLoading} required />
                                </FormControl>
                            </VStack>
                            <VStack mt={'10%'} spacing={'20px'}>
                                <Text color={messageColour} hidden={messageHidden} >{message}</Text>
                                <Button variant={!buttonDisabled && !verificationLoading ? 'Default' : 'solid'} w={{ base: 'xs', md: 'md', lg: 'lg' }} onClick={() => verifyOTP()} isDisabled={buttonDisabled} isLoading={verificationLoading} loadingText={'Verifying...'}>Verify</Button>
                            </VStack>
                        </Box>
                    </ScaleFade>
                </Box>
                <Spacer />
            </Box>
        </Box>
    )
}

export default VerifyEmail