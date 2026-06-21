import click
import os
import glob
from cipherveil_toolkit.utils import detect_format
from cipherveil_toolkit.modules import image, audio, qrcode, text, pdf, git

@click.group()
@click.option('--password', '-p', help='Password for AES-256 encryption/decryption.')
@click.pass_context
def cli(ctx, password):
    """CipherVeil Steganography Toolkit"""
    ctx.ensure_object(dict)
    ctx.obj['PASSWORD'] = password

@cli.group()
def encode():
    """Encode payload into various formats."""
    pass

@encode.command('image')
@click.argument('input_path', type=click.Path(exists=True))
@click.argument('payload', type=str)
@click.argument('output_path', type=click.Path())
@click.pass_context
def encode_image(ctx, input_path, payload, output_path):
    """Hide data inside an image (PNG/BMP)."""
    password = ctx.obj.get('PASSWORD')
    click.echo(f"Encoding image {input_path} to {output_path}...")
    image.encode(input_path, payload, output_path, password)
    click.echo("Done.")

@encode.command('audio')
@click.argument('input_path', type=click.Path(exists=True))
@click.argument('payload', type=str)
@click.argument('output_path', type=click.Path())
@click.pass_context
def encode_audio(ctx, input_path, payload, output_path):
    """Hide data inside an audio file (WAV/FLAC)."""
    password = ctx.obj.get('PASSWORD')
    click.echo(f"Encoding audio {input_path} to {output_path}...")
    audio.encode(input_path, payload, output_path, password)
    click.echo("Done.")

@encode.command('qrcode')
@click.argument('data', type=str)
@click.argument('payload', type=str)
@click.argument('output_path', type=click.Path())
@click.pass_context
def encode_qrcode(ctx, data, payload, output_path):
    """Hide data inside a QR code."""
    password = ctx.obj.get('PASSWORD')
    click.echo(f"Generating QR code with data '{data}' and hidden payload to {output_path}...")
    qrcode.encode(data, payload, output_path, password)
    click.echo("Done.")

@encode.command('text')
@click.argument('input_path', type=click.Path(exists=True))
@click.argument('payload', type=str)
@click.argument('output_path', type=click.Path())
@click.pass_context
def encode_text(ctx, input_path, payload, output_path):
    """Hide data inside text using zero-width characters."""
    password = ctx.obj.get('PASSWORD')
    click.echo(f"Encoding text {input_path} to {output_path}...")
    text.encode(input_path, payload, output_path, password)
    click.echo("Done.")

@encode.command('pdf')
@click.argument('input_path', type=click.Path(exists=True))
@click.argument('payload', type=str)
@click.argument('output_path', type=click.Path())
@click.pass_context
def encode_pdf(ctx, input_path, payload, output_path):
    """Hide data inside a PDF file."""
    password = ctx.obj.get('PASSWORD')
    click.echo(f"Encoding PDF {input_path} to {output_path}...")
    pdf.encode(input_path, payload, output_path, password)
    click.echo("Done.")

@encode.command('git')
@click.argument('repo_path', type=click.Path(exists=True))
@click.argument('payload', type=str)
@click.pass_context
def encode_git(ctx, repo_path, payload):
    """Hide data inside Git commit metadata."""
    password = ctx.obj.get('PASSWORD')
    click.echo(f"Encoding into git repo {repo_path}...")
    git.encode(repo_path, payload, password)
    click.echo("Done.")

@cli.command()
@click.argument('input_path', type=click.Path(exists=True))
@click.pass_context
def decode(ctx, input_path):
    """Automatically detect format and decode hidden payload."""
    password = ctx.obj.get('PASSWORD')
    fmt = detect_format(input_path)
    
    if fmt == 'unknown':
        click.echo("Could not determine file format.")
        return
        
    click.echo(f"Detected format: {fmt}. Decoding...")
    try:
        if fmt == 'image':
            result = image.decode(input_path, password)
        elif fmt == 'audio':
            result = audio.decode(input_path, password)
        elif fmt == 'pdf':
            result = pdf.decode(input_path, password)
        elif fmt == 'text':
            result = text.decode(input_path, password)
        elif fmt == 'git':
            result = git.decode(input_path, password)
        else:
            click.echo("Format not supported for decoding yet.")
            return
        click.echo(f"Decoded Payload: {result}")
    except Exception as e:
        click.echo(f"Error decoding: {e}")

@cli.command()
@click.argument('input_path', type=click.Path(exists=True))
def detect(input_path):
    """Detect file format and check for potential payloads."""
    fmt = detect_format(input_path)
    click.echo(f"Detected format: {fmt}")
    if fmt == 'image':
        from PIL import Image
        img = Image.open(input_path)
        cap = image.calculate_capacity(img)
        click.echo(f"Max Capacity: {cap} bytes")
    elif fmt == 'audio':
        import soundfile as sf
        data, _ = sf.read(input_path, dtype='int16')
        cap = audio.calculate_capacity(data)
        click.echo(f"Max Capacity: {cap} bytes")

@cli.command()
@click.option('--input-dir', required=True, type=click.Path(exists=True))
@click.option('--output-dir', required=True, type=click.Path())
@click.argument('payload', type=str)
@click.pass_context
def batch(ctx, input_dir, output_dir, payload):
    """Batch process a directory of files."""
    password = ctx.obj.get('PASSWORD')
    os.makedirs(output_dir, exist_ok=True)
    click.echo(f"Batch processing {input_dir} into {output_dir}...")
    
    for filename in os.listdir(input_dir):
        in_path = os.path.join(input_dir, filename)
        if not os.path.isfile(in_path):
            continue
            
        fmt = detect_format(in_path)
        out_path = os.path.join(output_dir, filename)
        
        try:
            if fmt == 'image':
                image.encode(in_path, payload, out_path, password)
                click.echo(f"Processed image: {filename}")
            elif fmt == 'audio':
                audio.encode(in_path, payload, out_path, password)
                click.echo(f"Processed audio: {filename}")
            elif fmt == 'text':
                text.encode(in_path, payload, out_path, password)
                click.echo(f"Processed text: {filename}")
            elif fmt == 'pdf':
                pdf.encode(in_path, payload, out_path, password)
                click.echo(f"Processed pdf: {filename}")
            else:
                click.echo(f"Skipping {filename} (unknown format)")
        except Exception as e:
            click.echo(f"Error processing {filename}: {e}")

if __name__ == '__main__':
    cli()
