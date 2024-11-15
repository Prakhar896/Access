import { useEffect, useState } from 'react'
import colouredLogo from '/logo/svg/logo-color.svg';
import { AbsoluteCenter, Box, Button, Center, FormControl, FormLabel, Heading, Image, Input, ScaleFade, Spacer, Spinner, Text, useMediaQuery, useToast, VStack } from '@chakra-ui/react';
import { useDispatch, useSelector } from 'react-redux';
import { Link, useNavigate } from 'react-router-dom';
import configureShowToast from '../components/showToast';
import server from '../networking';

function SignUp() {
    const navigate = useNavigate();
    const dispatch = useDispatch();
    const toast = useToast();
    const showToast = configureShowToast(toast);
    const { username, loaded, error } = useSelector(state => state.auth);
    const [limitedScreen] = useMediaQuery("(max-width: 800px)");

    const [requestOTPLoading, setRequestOTPLoading] = useState(false);
    const [usernameInput, setUsernameInput] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');

    const handleUsernameChange = (e) => { setUsernameInput(e.target.value); }
    const handleEmailChange = (e) => { setEmail(e.target.value); }
    const handlePasswordChange = (e) => { setPassword(e.target.value); }
    const handleConfirmPasswordChange = (e) => { setConfirmPassword(e.target.value); }

    const validateEmail = (text) => {
        return String(text)
            .toLowerCase()
            .match(
                /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|.(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
            );
    };

    const buttonDisabled = !usernameInput || !email || !password || !confirmPassword;

    const requestOTP = () => {
        if (!usernameInput || !email || !password || !confirmPassword) {
            showToast('Please fill in all fields', '', 'error');
            return;
        }
        if (validateEmail(email) === null) {
            showToast('Invalid email address', '', 'error');
            return;
        }
        if (password !== confirmPassword) {
            showToast('Passwords do not match', '', 'error');
            return;
        }

        const usernameString = usernameInput.trim();
        const emailAddress = email.trim();
        const passwordText = password.trim();
        setRequestOTPLoading(true);

        server.post('/identity/new', {
            username: usernameString,
            email: emailAddress,
            password: passwordText
        })
            .then(response => {
                if (response.status == 200) {
                    if (response.data && typeof response.data == "string") {
                        if (response.data.startsWith("SUCCESS")) {
                            showToast('Success', 'Please check your email for the verification link.', 'success');
                        } else if (response.data.startsWith("UERROR")) {
                            console.log("User error occurred in new identity creation; response:", response.data);
                            showToast("Something went wrong", response.data.substring("UERROR: ".length), 'error');
                        } else {
                            console.log("Unknown response from server in new identity creation; response:", response.data);
                            showToast("Something went wrong", "An error occurred. Please try again.", 'error');
                        }
                    } else {
                        console.log("Unexpected response in new identity creation; response:", response.data);
                        showToast("Something went wrong", "An error occurred. Please try again.", 'error');
                    }
                } else {
                    console.log("Non-200 status code in new identity creation; response:", response.data);
                    showToast("Something went wrong", "An error occurred. Please try again.", 'error');
                }

                setRequestOTPLoading(false);
            })
            .catch(err => {
                if (err.response && err.response.data && typeof err.response.data == "string") {
                    if (err.response.data.startsWith("UERROR")) {
                        console.log("User error occurred in new identity creation; response:", err.response.data);
                        showToast("Something went wrong", err.response.data.substring("UERROR: ".length), 'error');
                    } else if (err.response.data.startsWith("ERROR")) {
                        console.log("Error occurred in new identity creation; response:", err.response.data);
                        showToast("Something went wrong", "Failed to create account. Please try again.", 'error');
                    } else {
                        console.log("Unknown response from server in new identity creation; response:", err.response.data);
                        showToast("Something went wrong", "An error occurred. Please try again.", 'error');
                    }
                } else if (err.message) {
                    console.log("Error occurred in new identity creation; message:", err.message);
                    showToast("Something went wrong", "An error occurred. Please try again.", 'error');
                } else {
                    console.log("Unknown error occurred in new identity creation; error:", err);
                    showToast("Something went wrong", "An error occurred. Please try again.", 'error');
                }

                setRequestOTPLoading(false);
            })
    }

    useEffect(() => {
        if (username) {
            showToast("You're already signed in", '', 'info');
            navigate('/');
        }
    }, [username, loaded])

    if (!loaded) {
        return <Center h={'100vh'}><Spinner /></Center>
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
                            <Heading as={'h1'} size={'xl'}>Create an account</Heading>
                            <VStack spacing={4} mt={10}>
                                <FormControl id='username' required>
                                    <FormLabel>Username</FormLabel>
                                    <Input placeholder='e.g johndoe' type='text' w={{ base: 'xs', md: 'md', lg: 'lg' }} value={usernameInput} onChange={handleUsernameChange} required />
                                </FormControl>
                                <FormControl id='email' required>
                                    <FormLabel>Email</FormLabel>
                                    <Input placeholder='e.g john@example.com' type='email' w={{ base: 'xs', md: 'md', lg: 'lg' }} value={email} onChange={handleEmailChange} required />
                                </FormControl>
                                <FormControl id='password' required>
                                    <FormLabel>Password</FormLabel>
                                    <Input placeholder='Uppercase and numeric letters required' type='password' value={password} onChange={handlePasswordChange} required />
                                </FormControl>
                                <FormControl id='confirmPassword' required>
                                    <FormLabel>Confirm Password</FormLabel>
                                    <Input placeholder='Re-enter your password' type='password' value={confirmPassword} onChange={handleConfirmPasswordChange} required />
                                </FormControl>
                            </VStack>
                            <VStack mt={'10%'}>
                                <Text>Already have an account? <Button variant={'link'} color={'black'} onClick={() => navigate('/login')}>Login here.</Button></Text>
                                <Button variant={!buttonDisabled ? 'Default' : 'solid'} w={{ base: 'xs', md: 'md', lg: 'lg' }} onClick={requestOTP} isDisabled={buttonDisabled} isLoading={requestOTPLoading}>Get Started</Button>
                            </VStack>
                        </Box>
                    </ScaleFade>
                </Box>
                <Spacer />
            </Box>
        </Box>
    )
}

export default SignUp