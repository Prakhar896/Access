import React, { useEffect, useState } from 'react'
import { Box, Button, Heading, Spinner, Table, TableContainer, Tbody, Td, Text, Th, Thead, Tr, useToast } from '@chakra-ui/react';
import { Link as ChakraLink } from '@chakra-ui/react';
import { useSelector } from 'react-redux';
import withAuth from '../../components/hoc/withAuth';
import withNavbar from '../../components/hoc/withNavbar';
import server from '../../networking';
import configureShowToast from '../../components/showToast';
import CentredSpinner from '../../components/CentredSpinner';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faArrowDown, faCircleDown } from '@fortawesome/free-solid-svg-icons';

function Directory() {
    const backendURL = import.meta.env.VITE_BACKEND_URL;
    const { username, loaded } = useSelector(state => state.auth);
    const [filesData, setFilesData] = useState([]);
    const [retrievingFiles, setRetrievingFiles] = useState(true);
    const toast = useToast();
    const showToast = configureShowToast(toast);

    const downloadLinkFor = (file) => {
        return `${backendURL}/directory/file/${file}`;
    }

    const processFileData = (data) => {
        var newData = [];
        for (var file of data) {
            file["lastUpdate"] = file["lastUpdate"] ? new Date(file["lastUpdate"]).toLocaleString() : null;
            file["uploadedTimestamp"] = new Date(file["uploadedTimestamp"]).toLocaleString();

            newData.push(file);
        }

        return newData;
    }

    const fetchFiles = () => {
        setRetrievingFiles(true);
        server.get("/directory")
            .then(res => {
                if (res.status == 200) {
                    if (typeof res.data == "object" && !Array.isArray(res.data)) {
                        setFilesData(processFileData(Object.values(res.data)));
                        setRetrievingFiles(false);
                        return
                    } else {
                        console.log("Unexpected response format when retrieving files; response: ", res.data);
                    }
                } else {
                    console.log("Non-200 status code received in retrieving files; response: ", res.data);
                }
                showToast("Something went wrong", "Couldn't retrieves files. Please try again.", "error");
            })
            .catch(err => {
                if (err.response && err.response.data && typeof err.response.data == "string") {
                    if (err.response.data.startsWith("UERROR")) {
                        console.log("User error occurred in retrieving files; response: ", err.response.data);
                        showToast("Something went wrong", err.response.data.substring("UERROR: ".length), "error");
                        return
                    } else {
                        console.log("Unknown response from server in retrieving files; response: ", err.response.data);
                    }
                } else if (err.message && typeof err.message == "string") {
                    console.log("Error occurred in retrieving files; message: ", err.message);
                } else {
                    console.log("Unknown error occurred in retrieving files; error: ", err);
                }
                showToast("Something went wrong", "Couldn't retrieves files. Please try again.", "error");
            })
    }

    useEffect(() => {
        if (loaded) {
            fetchFiles();
        }
    }, [loaded]);

    useEffect(() => {
        console.log(filesData);
    }, [filesData]);

    return (
        <Box display={'flex'} flexDir={'column'} justifyContent={'left'} m={'1rem'} p={'10px'}>
            <Heading as={'h1'} fontSize={'3xl'} fontFamily={'Ubuntu'}>My Files</Heading>
            {retrievingFiles && (
                <Box display={'flex'} justifyContent={'left'} alignItems={'center'} mt={'5%'}>
                    <Spinner />
                </Box>
            )}
            {!retrievingFiles && filesData.length == 0 && <Text>No files found.</Text>}
            {!retrievingFiles && filesData.length > 0 && (
                <TableContainer mt={{ base: '15px', md: '20px', lg: '25px' }}>
                    <Table variant='simple'>
                        <Thead>
                            <Tr>
                                <Th>Name</Th>
                                <Th>Modified</Th>
                                <Th>Uploaded</Th>
                                <Th>Actions</Th>
                            </Tr>
                        </Thead>
                        <Tbody>
                            {filesData.map((file, index) => (
                                <Tr key={index}>
                                    <Td>
                                        <ChakraLink href={downloadLinkFor(file.name)} color={'blue.500'}>{file.name}</ChakraLink>
                                    </Td>
                                    <Td>{file.lastUpdate ?? "Unavailable"}</Td>
                                    <Td>{file.uploadedTimestamp}</Td>
                                    <Td>
                                        <Button onClick={() => { location.href = downloadLinkFor(file.name); }} variant={'ghost'} size={'md'}>
                                            <FontAwesomeIcon icon={faCircleDown} />
                                        </Button>
                                    </Td>
                                </Tr>
                            ))}
                        </Tbody>
                    </Table>
                </TableContainer>
            )}
        </Box>
    )
}

export default withAuth(withNavbar(Directory));