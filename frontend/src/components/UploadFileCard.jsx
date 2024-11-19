import { Button, Card, Spacer, Spinner, Text } from '@chakra-ui/react'
import { BsFillCheckCircleFill } from 'react-icons/bs';

function UploadFileCard({ index, fileName, uploading, uploadResults, handleRemoveFile }) {
    const uploadMessage = typeof uploadResults == "object" && uploadResults[fileName] !== undefined ? uploadResults[fileName] : null;
    const success = uploadMessage && uploadMessage.startsWith("SUCCESS");

    return (
        <Card key={index} mb={2} padding={"13px"} display="flex" flexDirection={"row"} alignItems={'center'} justifyContent={"space-between"}>
            {uploading && <Spinner />}
            {success && (
                <BsFillCheckCircleFill color={'lime'} size={'20px'} />
            )}
            <Text fontSize={"15px"} ml={"20px"} textOverflow={"ellipsis"}>
                {fileName}
            </Text>
            {!uploading ? (
                <Button onClick={() => handleRemoveFile(index)} color={'red'}>
                    Remove
                </Button>
            ) : (
                <Spacer />
            )}
        </Card>
    )
}

export default UploadFileCard