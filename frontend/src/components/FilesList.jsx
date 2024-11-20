import { Table, TableContainer, Tbody, Td, Text, Th, Thead, Tr, Link as ChakraLink, Button, Box, Spinner, useMediaQuery, HStack } from '@chakra-ui/react';
import { faCircleDown } from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import React from 'react'
import FileActions from './FileActions';
import server from '../networking';

function FilesList({ filesData, retrieving }) {
    const backendURL = server.defaults.baseURL;
    const [limitedScreen] = useMediaQuery("(max-width: 800px)");

    const downloadLinkFor = (file) => {
        return `${backendURL}/directory/file/${file}`;
    }

    if (retrieving == true) {
        return (
            <Box display={'flex'} justifyContent={'left'} alignItems={'center'} mt={'5%'}>
                <Spinner />
            </Box>
        )
    }

    if (!retrieving && filesData.length <= 0) {
        return <Box display={'flex'} justifyContent={'left'} alignItems={'center'} mt={'5%'}>
            <Text>No files found.</Text>
        </Box>
    }

    return (
        <TableContainer mt={{ base: '15px', md: '20px', lg: '25px' }} w={limitedScreen && '100%'} boxShadow={'xl'} border={'1px solid #4d5566'} borderRadius={'10px'} >
            <Table variant='simple'>
                <Thead>
                    <Tr>
                        <Th>Name</Th>
                        {!limitedScreen && (
                            <>
                                <Th>Modified</Th>
                                <Th>Uploaded</Th>
                            </>
                        )}
                        <Th>Actions</Th>
                    </Tr>
                </Thead>
                <Tbody>
                    {filesData.map((file, index) => (
                        <Tr key={index}>
                            <Td>
                                {file.name ? (
                                    <ChakraLink href={downloadLinkFor(file.name)} color={'blue.500'} fontSize={{ base: 'sm', md: 'md', lg: 'lg' }}><Text maxW={{ base: '200px', md: '300px', lg: 'fit-content' }} isTruncated>{file.name}</Text></ChakraLink>
                                ) : (
                                    <Text color={'red'}>Unavailable</Text>
                                )}
                            </Td>
                            {!limitedScreen && (
                                <>
                                    <Td>{file.lastUpdate ?? "Unavailable"}</Td>
                                    <Td>{file.uploadedTimestamp}</Td>
                                </>
                            )}
                            <Td>
                                <HStack w={'100%'} ml={"10px"}>
                                    <FileActions fileData={file} downloadLinkFor={downloadLinkFor} />
                                </HStack>
                            </Td>
                        </Tr>
                    ))}
                </Tbody>
            </Table>
        </TableContainer>
    )
}

export default FilesList